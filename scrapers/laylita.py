"""Adaptador: Layla Pujol (Equador, laylita.com) — via crawl BFS a partir de /recipes/index.

Sondagem: o site é WordPress/Yoast, mas o sitemap.xml é inútil para receitas — o
post-sitemap tem 10 URLs antigas (blog/wine) e o page-sitemap só tem páginas
institucionais (/reviews/, /lifestyle/, ...). As receitas reais NÃO estão no sitemap.

As receitas vivem em https://www.laylita.com/recipes/<slug> (exatamente 2 segmentos).
A página /recipes/index é um índice completo (~500+ links de receita), então um crawl
BFS a partir dela cobre o catálogo. Excluímos páginas de categoria/listagem
(/recipes/category/..., /recipes/index, /recipes/about) e os roundups/landing pages
(slugs terminando em "-recipes"/"-meals"/"-soups" e um punhado de páginas curadas).
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Layla Pujol"
SITE = "laylita.com"
TECNICAS = ["crawl"]
SEEDS = ["https://www.laylita.com/recipes/index", "https://www.laylita.com/recipes/"]

# Slugs de 2 segmentos sob /recipes/ que NÃO são receitas individuais
# (navegação, índice, páginas curadas de categoria).
_NAO_RECEITA = {
    "index", "about", "blog", "category", "top-latin-recipes",
    "all-about-empanadas", "ecuadorian-recipes", "ecuadorian-soups",
    "ecuadorian-main-meals", "ecuadorian-street-food",
    "ecuadorian-appetizers-and-snacks", "traditional-ecuadorian-breakfast-dishes",
    "plantain-recipes", "ceviche-recipes", "fish-and-seafood-recipes",
    "latin-desserts-and-sweets",
}

# Sufixos típicos de páginas de coletânea/landing (não receita única).
_SUFIXOS_LISTAGEM = ("-recipes", "-meals", "-soups", "-dishes-collection")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "laylita.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita individual: /recipes/<slug>  (exatamente 2 segmentos)
    if len(partes) != 2 or partes[0] != "recipes":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(slug.endswith(suf) for suf in _SUFIXOS_LISTAGEM):
        return False
    return True


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite)
