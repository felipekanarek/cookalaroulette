"""Adaptador: Difford's Guide (Reino Unido) — COQUETÉIS, via sitemap.

diffordsguide.com é um portal enorme de coquetéis (acervo de milhares de drinks),
mas também publica bares, fórum, artigos, ingredientes e marcas. A marca é o "chef".

O /sitemap.xml é um índice que aponta sitemaps por seção:
  gb.xml, bar.xml, cocktail.xml, forum.xml, cocktail-user-generated.xml
Seguimos APENAS o `cocktail.xml` (via `sub_filtro`), que lista as receitas de drink.

As páginas de receita individual têm o padrão estável:
  https://www.diffordsguide.com/cocktails/recipe/<id>/<slug>
Ex.: /cocktails/recipe/35/alexander
`_e_receita` exige esse path com id numérico + slug, excluindo as páginas-índice
do próprio sitemap de coquetéis (/cocktails, /cocktails/search, /cocktails/how-to-make,
/cocktails/20-best, /cocktails/most-viewed, /cocktails/directory, etc.) e tudo o mais
do portal (bares, fórum, ingredientes, marcas, artigos).

Observação de sondagem: /sitemap.xml e /robots.txt dão 403 para o curl padrão, mas o
User-Agent do projeto (base.HEADERS) é liberado normalmente (200). Por isso o sitemap
HTTP comum funciona — não é preciso navegador.

Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Difford's Guide"
SITE = "diffordsguide.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.diffordsguide.com"

# Receita de coquetel = /cocktails/recipe/<id>/<slug>
_PADRAO_RECEITA = re.compile(r"^/cocktails/recipe/\d+/[a-z0-9][a-z0-9-]*$", re.IGNORECASE)


# Dentro do índice de sitemaps, só seguimos o de coquetéis (cocktail.xml),
# evitando gb / bar / forum / cocktail-user-generated.
def _sub_sitemap_de_coqueteis(url: str) -> bool:
    return url.lower().rstrip("/").endswith("/cocktail.xml")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    return bool(_PADRAO_RECEITA.match(p.path.rstrip("/")))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_coqueteis)
