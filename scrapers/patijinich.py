"""Adaptador: Pati Jinich (México) — via crawl BFS a partir de /recipes/.

O post-sitemap mistura receitas com muitas aparições na mídia (cbs/kcrw/npr/...), poluindo
o resultado. Em vez disso, partimos da página /recipes/ (lista receitas reais) e seguimos
os links de "receitas relacionadas" — assim só trafegamos por páginas de receita, evitando
os posts de mídia.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Pati Jinich"
SITE = "patijinich.com"
TECNICAS = ["crawl"]
SEEDS = ["https://patijinich.com/recipes/"]

_NAO_RECEITA = {
    "recipes", "recommended-products", "terms", "privacy-policy", "about", "about-pati",
    "contact", "shop", "books", "book", "episodes", "blog", "press", "tv", "videos",
    "newsletter", "search", "events", "travel", "subscribe", "media", "faq", "post",
    "collection", "cookbook", "news-events", "es", "en", "recommended-products",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "patijinich.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case (exclui underscore)


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite)
