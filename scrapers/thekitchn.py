"""Adaptador: The Kitchn — via Internet Archive (Wayback).

The Kitchn é um portal editorial GRANDE (Apartment Therapy Media): mistura muitíssimo
artigo, notícia, review e guia "how-to" com receitas. O /sitemap.xml fica atrás de um WAF
(Varnish/Fastly + desafio "Please verify you are human"): GET devolve 403/página de desafio
mesmo com User-Agent de navegador. As páginas de receita em si abrem normalmente para
humanos (200/308), e o app só precisa da URL para redirecionar — então descobrimos as URLs
pela API CDX do Internet Archive, sem tocar no site (Princípio III/VII). 403 = vivo.

A separação receita × artigo é limpa e fica TODA na URL: as receitas têm um prefixo de tipo
no slug e terminam num id numérico:

    /recipe-<slug>-<id>     -> RECEITA   (ex.: /recipe-10-minute-black-bean-tacos-233042)
    /how-to-...             -> guia      (excluído)
    /the-best-... , /...    -> artigo/notícia/review  (excluído, não tem prefixo recipe-)

Basta exigir o caminho canônico `^/recipe-<slug>-<id>$` (segmento único, termina em id). Isso
descarta de uma vez todo o ruído que o CDX captura de JSON/JS inline (slugs com %22, %5C,
truncados sem id final, /print, /amp etc.) e qualquer conteúdo que não seja receita.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urlparse

import requests

from . import base

CHEF = "The Kitchn"
SITE = "thekitchn.com"
TECNICAS = ["wayback"]
DOMINIO = "thekitchn.com"

# Receita canônica: /recipe-<slug-kebab>-<id-numérico>  (segmento único de caminho).
# O id final separa a receita real do ruído de JS/JSON do índice do Wayback; o lookahead
# (?=[a-z0-9-]*[a-z]) exige ao menos UMA letra no slug, descartando placeholders como
# /recipe-1-22620, /recipe-2-24058 (slug numérico puro, sem nome de prato).
_RECEITA_RE = re.compile(r"^/recipe-(?=[a-z0-9-]*[a-z])[a-z0-9]+(?:-[a-z0-9]+)*-\d+$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla do índice Wayback)
    if "//" in p.path:
        return False
    return bool(_RECEITA_RE.match(p.path))


def coletar(limite: int) -> list[dict]:
    # LACUNA no base.py: base.coletar_por_wayback usa matchType=domain + filter=original:
    # (regex anchored). Para thekitchn.com esse caminho falha de duas formas:
    #   (a) sem filtro, a resposta ordenada por urlkey vem CHEIA de ruído de JS/JSON inline
    #       capturado pelo Wayback (/%22//admin.../recipe-...%22/AllSites.require etc.) — as
    #       primeiras ~500 linhas não têm UMA receita canônica;
    #   (b) com filtro anchored, o CDX varre o índice do domínio inteiro e dá 504 (timeout).
    # Solução sem tocar no base: consultar o CDX por PREFIXO de caminho (url=<dom>/recipe-*,
    # matchType=prefix). Esse índice é direto/rápido e devolve só URLs sob /recipe-..., onde
    # _e_receita filtra para a forma canônica /recipe-<slug>-<id>. Reusa os helpers do base
    # (fazer_registro/registro_valido/humanizar_slug/HEADERS).
    # url=<dom>/recipe-* sem matchType explícito: o '*' aciona matchType=prefix
    # automaticamente (combinar '*' com matchType=prefix faria o '*' virar literal → vazio).
    cdx = ("https://web.archive.org/cdx/search/cdx?url=" + DOMINIO +
           "/recipe-*&collapse=urlkey&output=json&fl=original&limit=" +
           str(max(2000, limite * 40)))
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
    for linha in linhas[1:]:  # pula o cabeçalho
        bruta = linha[0] if isinstance(linha, list) else linha
        url = bruta.split("#")[0].split("?")[0].rstrip("/")  # tira query/fragmento
        if url.startswith("http://"):
            url = "https://" + url[len("http://"):]          # normaliza esquema
        url = url.replace(":80/", "/", 1)                    # tira porta do índice Wayback
        if url in vistos or not _e_receita(url):
            continue
        vistos.add(url)
        # humanizar_slug devolve "Recipe Black Bean Tacos ..." (o prefixo de tipo recipe-
        # vira palavra) — tiramos o "Recipe " inicial para o título ficar com o nome do prato.
        titulo = re.sub(r"^Recipe\s+", "", base.humanizar_slug(url)).strip() or "(sem título)"
        r = base.fazer_registro(CHEF, SITE, titulo, url)
        if base.registro_valido(r):
            registros.append(r)
        if len(registros) >= limite:
            break
    return registros
