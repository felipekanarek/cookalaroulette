"""Adaptador: The Spanish Chef (Omar Allibhoy, Espanha) — via sitemap.

Site WordPress com sitemap Yoast em /sitemap_index.xml (atrás de Cloudflare, mas o
cliente HTTP comum passa). As receitas ficam em https://www.thespanishchef.com/recipes/<slug>/;
o post-sitemap mistura posts de /blog/<slug>/ (aparições na mídia), filtrados fora.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Omar Allibhoy"
SITE = "thespanishchef.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.thespanishchef.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page/product/category/tag/author-sitemap (institucional, loja, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # caminho /recipes/<slug>/ — receita individual (não /blog/, não /recipes/ raiz)
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 2 or partes[0] != "recipes":
        return False
    slug = partes[1].lower()
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
