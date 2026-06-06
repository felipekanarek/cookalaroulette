"""Adaptador: RecipeTin Eats (Nagi Maehashi) — via sitemap.

As receitas ficam em slug de raiz: https://www.recipetineats.com/<slug>/
(aprendizado do briefing: a página /recipes/ só mostra as recentes; o sitemap traz tudo).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Nagi Maehashi"
SITE = "recipetineats.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.recipetineats.com"

# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap (páginas institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (mesmo dentro do post-sitemap).
_NAO_RECEITA = {
    "about", "about-nagi-and-dozer", "contact", "privacy-policy", "terms",
    "recipes", "category", "tag", "subscribe", "shop", "cookbooks", "my-account",
    "web-stories", "search", "newsletter", "faq", "press", "wprm_print",
    "blog", "new-york-food-map", "rte-meal-plans", "members", "gift",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento de caminho: /slug/  ou  /slug
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
