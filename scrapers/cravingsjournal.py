"""Adaptador: Cravings Journal (Lorena Salinas, Peru) — via listagem de categorias.

O site (WordPress + Cloudflare, mas o HTTP comum passa) tem sitemap, porém o
`post-sitemap.xml` mistura receitas com posts de lifestyle/travel/beauty no MESMO
padrão de slug-raiz (`/slug/`) — impossível separar só pela URL. As páginas de
categoria de receita (`/category/recipes/<sub>/`) são server-rendered e listam só
receitas, então usamos elas como índice (`coletar_por_listagem`): isso filtra o
ruído não-culinário na origem. O filtro `_e_receita` ainda exclui institucionais.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Lorena Salinas"
SITE = "cravingsjournal.com"
TECNICAS = ["listagem"]
BASE_URL = "https://cravingsjournal.com"

# Subcategorias de receita (do category-sitemap.xml). Cada uma é uma página-índice
# que lista receitas; varremos algumas páginas de cada uma para cobrir o acervo.
_CATEGORIAS_RECEITA = [
    "appetizers", "basic-recipes", "bread", "breakfast-and-brunch",
    "christmas-recipes", "cookies", "desserts", "drinks-and-cocktails",
    "healthy-recipes", "icecream", "main-courses", "peruvian-dishes",
    "salads", "sandwiches", "soups", "sourdough", "tea-time",
    "vegetarian-dishes",
]


def _seeds() -> list:
    seeds = [BASE_URL + "/category/recipes/"]
    # paginação da categoria-mãe (cobre o grosso do acervo)
    for n in range(2, 12):
        seeds.append(BASE_URL + f"/category/recipes/page/{n}/")
    for sub in _CATEGORIAS_RECEITA:
        seeds.append(BASE_URL + f"/category/recipes/{sub}/")
    return seeds


# Slugs-raiz que NÃO são receitas (institucionais / utilitários do WordPress).
_NAO_RECEITA = {
    "about", "about-me", "contact", "feed", "wp-json", "wp-login", "wp-admin",
    "privacy-policy", "terms", "shop", "subscribe", "newsletter", "search",
    "cart", "checkout", "my-account", "category", "tag", "author", "page",
    "recipes", "blog", "ebooks", "recipe-ebooks", "amazon-shop", "press",
    "work-with-me", "faq", "home", "es", "en",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:  # receita fica no slug-raiz: /slug/
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    # kebab-case com >=2 palavras (nomes de prato); evita páginas de 1 termo genéricas
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)+$", slug))


def coletar(limite: int) -> list:
    return base.coletar_por_listagem(_seeds(), CHEF, SITE, _e_receita, limite)
