"""Adaptador: Natasha's Kitchen (Ucrânia/EUA) — via sitemap (WordPress/Yoast).

sitemap_index.xml acessível; receitas em slug de raiz. Segue sub-sitemaps de posts e
filtra slugs kebab-case, descartando páginas/tips conhecidos.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Natasha Kravchuk"
SITE = "natashaskitchen.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://natashaskitchen.com"

_NAO_RECEITA = {
    "about", "about-us", "contact", "privacy-policy", "terms", "recipes", "category",
    "tag", "favorites", "cookbook", "shop", "subscribe", "newsletter", "search", "blog",
    "web-stories", "faq", "press", "how-to", "cooking-tips", "amazon-shop",
}


def _sub_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "natashaskitchen.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    # as receitas da Natasha's Kitchen têm o sufixo "-recipe" no slug; tips/how-tos não
    if "recipe" not in slug:
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite, sub_filtro=_sub_posts)
