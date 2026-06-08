"""Adaptador: The Spruce Eats (EUA, Dotdash Meredith) — via Internet Archive (Wayback).

A marca é o "chef" (portal editorial da Dotdash Meredith). O site fica atrás de
Cloudflare: o /sitemap.xml RAIZ abre (200, só um índice com um sub-sitemap), mas o
sub-sitemap real (/sitemap_1.xml) cai num desafio "Just a moment..." (403) tanto via
curl quanto via requests — não dá pra ler o catálogo pelo sitemap. As páginas de receita
em si abrem normalmente para humanos; o app só precisa da URL para redirecionar. Então
descobrimos as URLs pela API CDX do Internet Archive, sem tocar no site (Princípio III/VII).
403 = vivo, não bloqueio fatal.

Estrutura de URL (padrão Dotdash): TUDO mora no slug-raiz e termina num id numérico —
https://www.thespruceeats.com/<slug>-<id>. O sinal confiável de RECEITA INDIVIDUAL é o
sufixo SINGULAR `-recipe-<id>` no fim do slug:

    /aash-reshteh-recipe-5219123          -> RECEITA   (singular -recipe-<id>)
    /24-hour-gravy-recipe-5201711         -> RECEITA   (número no nome do prato, ok)
    /10-apple-recipes-for-fall-7629081    -> roundup    (plural -recipes-, excluído)
    /a-recipe-for-making-cold-smoked-...  -> artigo     (-recipe- no meio, não no fim, excluído)
    /how-to-... , /the-best-... , guias   -> artigo/guia (não terminam em -recipe-<id>)

Basta exigir o caminho canônico `^/<slug>-recipe-<id>$` (segmento único, termina em
`-recipe-` + id numérico). Isso descarta roundups (plural), artigos, guias e o ruído de
JSON/JS inline que o índice do Wayback captura (slugs com %22, ?url=, /print etc.).
"""
from __future__ import annotations

import re
import time
from urllib.parse import urlparse

import requests

from . import base

CHEF = "The Spruce Eats"
SITE = "thespruceeats.com"
TECNICAS = ["wayback"]
DOMINIO = "thespruceeats.com"

# Receita canônica: /<slug-kebab>-recipe-<id-numérico>  (segmento único de caminho).
# - o sufixo SINGULAR "-recipe-" separa receita de roundup ("-recipes-", plural);
# - o id numérico final tem que vir logo após "-recipe-" (descarta "a-recipe-for-..."
#   onde "-recipe-" aparece no meio do slug);
# - o lookahead (?=[a-z0-9-]*[a-z]) exige ao menos UMA letra no slug, evitando
#   placeholders numéricos puros.
_RECEITA_RE = re.compile(r"^/(?=[a-z0-9-]*[a-z])[a-z0-9]+(?:-[a-z0-9]+)*-recipe-\d+$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla do índice Wayback)
    if "//" in p.path:
        return False
    return bool(_RECEITA_RE.match(p.path))


def coletar(limite: int) -> list[dict]:
    # LACUNA no base.py: base.coletar_por_wayback monta o título com humanizar_slug, que
    # aqui deixaria a palavra "Recipe" no fim ("Adobo Sauce Recipe") — o sufixo de tipo
    # -recipe- vira palavra. Replicamos o fluxo wayback (mesmo CDX/normalização do base)
    # mas limpamos o "Recipe" final do título. Reusa os helpers do base
    # (HEADERS/humanizar_slug/fazer_registro/registro_valido).
    #
    # Filtro no servidor por slugs que contêm "-recipe-<id>" reduz a resposta (o domínio é
    # grande); _e_receita faz o filtro fino (singular vs. plural, id no fim). limit baixo o
    # bastante p/ o CDX não dar timeout, com folga p/ dedup de variantes ?query.
    cdx = ("http://web.archive.org/cdx/search/cdx?url=" + DOMINIO +
           "&matchType=domain&collapse=urlkey&output=json&fl=original&limit=" +
           str(max(2000, limite * 40)) +
           "&filter=original:.*-recipe-[0-9].*")
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
        # humanizar_slug já tira o id final, mas deixa "... Recipe" no fim (o sufixo de
        # tipo vira palavra) — removemos para o título ficar com o nome do prato.
        titulo = re.sub(r"\s+Recipe$", "", base.humanizar_slug(url)).strip() or "(sem título)"
        r = base.fazer_registro(CHEF, SITE, titulo, url)
        if base.registro_valido(r):
            registros.append(r)
        if len(registros) >= limite:
            break
    return registros
