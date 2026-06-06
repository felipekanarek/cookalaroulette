"""Adaptador: Donal Skehan (Irlanda) — via sitemap dedicado de receitas.

O site é WordPress/Yoast e expõe um sub-sitemap próprio só de receitas
(recipes-sitemap.xml / recipes-sitemap2.xml). As receitas individuais ficam em
https://donalskehan.com/recipes/<slug>/ (exatamente 2 segmentos de caminho).
Restringimos a coleta a esses sub-sitemaps para evitar posts, páginas, vídeos, etc.
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Donal Skehan"
SITE = "donalskehan.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://donalskehan.com"


# Só seguimos os sub-sitemaps de RECEITAS (recipes-sitemap.xml, recipes-sitemap2.xml),
# ignorando post/page/tv/books/blog/video/category/tag/ingredient-sitemaps.
def _sub_sitemap_de_receitas(url: str) -> bool:
    return "recipes-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # /recipes/<slug>/ — exatamente dois segmentos, o primeiro é "recipes"
    partes = [s for s in p.path.split("/") if s]
    return len(partes) == 2 and partes[0] == "recipes"


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
