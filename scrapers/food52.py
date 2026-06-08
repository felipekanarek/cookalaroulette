"""Adaptador: Food52 (marca, EUA) — editorial + comunidade, via Internet Archive (wayback).

food52.com fica 100% atrás do Vercel Security Checkpoint: o cliente HTTP comum (e até
robots.txt/sitemap.xml) devolve 429 com "x-vercel-mitigated: challenge". Como só
precisamos da URL para redirecionar (Princípio III), descobrimos o catálogo pela API CDX
do Internet Archive — sem tocar no site. As páginas de receita seguem vivas para humanos
(retornam 429 ao bot, que a verificação trata como "existe").

Acervo enorme e MUITO ruidoso (comunidade + comentários scrapados que viraram URLs
quebradas no Archive: `/recipes/%5C...`, `/recipes/...%E2%80%9D`, `/recipes/&callback=`,
e milhares de `_next/data/<hash>/recipes/<slug>.json`). A forma canônica de uma receita é
`/recipes/<id>-<slug>` (id numérico). Filtramos restritivamente por esse padrão e
excluímos blog/story/loja/perguntas/categorias/`_next`/`.json` e o lixo de comentários.

NOTA (lacuna no base.py — relatada, não corrigida): `base.coletar_por_wayback` consulta o
CDX com `matchType=domain`, que neste domínio gigante (1) estoura 504 (timeout no índice
inteiro) e (2) inunda a resposta com `_next/data/.../recipes/<id>-<slug>.json`, afogando as
URLs reais dentro do `limite`. A consulta `matchType=prefix` em `food52.com/recipes`
retorna limpa e rápida (~3 s). Como só posso editar este arquivo, replico aqui o miolo do
helper (retry/backoff + dedup + normalização de esquema), porém com `matchType=prefix` e
SEM `filter=` server-side (o `filter` regex também derruba o CDX por timeout neste índice);
todo o saneamento é feito localmente em `_e_receita`. Reutilizo os demais helpers de base.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urlparse, unquote

import requests

from . import base

CHEF = "Food52"
SITE = "food52.com"
TECNICAS = ["wayback"]

# Forma canônica: /recipes/<id>-<slug>, id numérico, slug iniciando por letra (kebab-case).
# Ex.: /recipes/10002-skillet-lasagna
_RECEITA = re.compile(r"^/recipes/[0-9]+-[a-z][a-z0-9-]*$")

# Caracteres que denunciam lixo de comentário scrapado virado em URL no Archive.
_LIXO = ('"', "'", "\\", "<", ">", "!", "=", "&", "(", ")", "..", ",", " ")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    caminho = p.path
    # `_next/data/<hash>/recipes/<slug>.json` é payload de dados, não a página.
    if "_next" in caminho or caminho.endswith(".json"):
        return False
    if caminho != unquote(caminho):  # tinha %-encoding → não é slug real
        return False
    if any(c in caminho for c in _LIXO):
        return False
    return bool(_RECEITA.match(caminho.lower()))


def coletar(limite: int) -> list[dict]:
    # matchType=prefix em /recipes é rápido e limpo; SEM filter= server-side (derruba o CDX).
    cdx = ("http://web.archive.org/cdx/search/cdx?url=" + SITE + "/recipes"
           "&matchType=prefix&collapse=urlkey&output=json&fl=original&limit="
           + str(max(2000, limite * 30)))
    linhas = None
    for tentativa in range(4):
        try:
            resp = requests.get(cdx, headers=base.HEADERS, timeout=120)
            resp.raise_for_status()
            linhas = resp.json()
            break
        except Exception:
            time.sleep(4 * (tentativa + 1))
    if not linhas:
        return []

    vistos = set()
    registros: list[dict] = []
    for linha in linhas[1:]:  # pula o cabeçalho ["original"]
        bruta = linha[0] if isinstance(linha, list) else linha
        url = bruta.split("#")[0].split("?")[0].rstrip("/")  # remove query/fragmento
        if url.startswith("http://"):
            url = "https://" + url[len("http://"):]          # normaliza esquema
        if url in vistos or not _e_receita(url):
            continue
        vistos.add(url)
        # humanizar_slug só remove id numérico FINAL; aqui o id é PREFIXO
        # (/recipes/10002-skillet-lasagna) → tira o "<id>-" antes de humanizar.
        slug_sem_id = re.sub(r"^[0-9]+-", "", url.rstrip("/").rsplit("/", 1)[-1])
        titulo = base.humanizar_slug("https://x/" + slug_sem_id)
        r = base.fazer_registro(CHEF, SITE, titulo, url)
        if base.registro_valido(r):
            registros.append(r)
        if len(registros) >= limite:
            break
    return registros
