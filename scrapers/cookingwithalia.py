"""Adaptador: Cooking with Alia (Alia Laskar — Marrocos) — via sitemap.

Site WordPress com sitemap Yoast acessível por HTTP comum
(robots.txt → /sitemap_index.xml). As receitas são posts em slug de raiz:
https://www.cookingwithalia.com/<slug>/  (ex.: /souffle/, /moroccan-crepes-baghrir/,
/video-makrout-moroccan-date-cookie/). Muitos posts são episódios de vídeo do canal,
mas a página de receita vive no próprio site — é dela que pegamos a URL.

Só seguimos os post-sitemaps (onde estão as receitas), ignorando page/category/tag/
author/attachment-sitemaps (institucional, taxonomia, mídia). Excluímos o índice
/recipes/ e os posts-listicle "blog top 10". As versões traduzidas (/ar/, /fr/) têm
caminho com 2+ segmentos e são naturalmente descartadas pelo filtro de slug único.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse, unquote

from . import base

CHEF = "Alia Laskar"
SITE = "cookingwithalia.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.cookingwithalia.com"


# Só os sub-sitemaps de POSTS trazem receitas; evita page/category/tag/author/attachment.
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (índice, listicles de blog, institucional).
_NAO_RECEITA = {
    "recipes", "about", "contact", "press", "blogs", "blog", "conversions",
    "special-series", "clean-eating", "my-books", "privacy-policy",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento → descarta traduções /ar/<slug>, /fr/<slug>
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = unquote(partes[0]).lower()
    if slug in _NAO_RECEITA:
        return False
    # listicles "blog top 10" não são receita individual
    if "blog-top-10" in slug:
        return False
    return bool(slug)


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
