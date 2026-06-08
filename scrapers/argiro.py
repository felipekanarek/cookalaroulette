"""Adaptador: Argiro Barbarigou (Grécia) — via sitemap.

WordPress + Yoast SEO: sitemap_index.xml → recipe-sitemap*.xml (sitemaps DEDICADOS de
receitas, ~3,3k URLs). As receitas ficam em https://www.argiro.gr/recipe/<slug>/, com
slug romanizado do grego (kebab-case). Alguns slugs trazem o "micro sign" percent-encoded
(%c2%b5, usado no lugar de μ), ex.: /recipe/salata-%c2%b5e-tono-apo-tin-argyro/ — por isso
o filtro usa unquote + re.UNICODE (inspirado em yejiskitchenstories.py).

Como há sitemap dedicado de receitas, o sub_filtro evita post/page/category/taxonomia.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse, unquote

from . import base

CHEF = "Argiro Barbarigou"
SITE = "argiro.gr"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.argiro.gr"


# Só seguimos os sub-sitemaps DEDICADOS a receitas (recipe-sitemap.xml, recipe-sitemap2.xml,
# ...), evitando recipe-CATEGORY-sitemap, post-sitemap, page-sitemap e taxonomias.
def _sub_sitemap_de_receitas(url: str) -> bool:
    return bool(re.search(r"/recipe-sitemap\d*\.xml$", url.lower()))


# Slug = palavras separadas por hífen, aceitando letras Unicode e dígitos (após unquote
# o %c2%b5 vira o caractere µ, uma letra). \w cobre [a-zA-Z0-9_] + letras Unicode; barramos
# "_" e exigimos pelo menos 2 segmentos (receitas têm nome composto).
_SLUG = re.compile(r"^[^\W_]+(?:-[^\W_]+)+$", re.UNICODE)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita individual: exatamente /recipe/<slug>/
    if len(partes) != 2 or partes[0] != "recipe":
        return False
    slug = unquote(partes[1]).lower()  # %c2%b5 -> µ
    if slug.isdigit():
        return False
    return bool(_SLUG.match(slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
