"""Adaptador: Ozoz Sokoh (Kitchen Butterfly, Nigéria) — via crawl de listagem.

Site WordPress/Yoast com sitemap acessível, MAS é um blog pessoal: o post-sitemap
(~1000 posts em slug de raiz) mistura receitas com muito conteúdo não-receita (relatos
de viagem, ensaios, resenhas de livros, "photo essays", press). O slug de raiz é, então,
ambíguo demais para um filtro confiável via sitemap.

Estratégia: crawl BFS a partir das páginas de CATEGORIA de receitas (chicken-recipes,
soups, stews-sauces, etc.), trafegando só por posts ligados a essas categorias. Mesmo
assim sobra ruído (ensaios sobre ingredientes aparecem nas categorias), então um denylist
de slugs institucionais/navegação corta o óbvio. Receitas em slug de raiz:
https://www.kitchenbutterfly.com/<slug>/.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Ozoz Sokoh"
SITE = "kitchenbutterfly.com"
TECNICAS = ["crawl"]

# Páginas de categoria que listam receitas reais (evita culinary-travel, history-heritage,
# food-in-books e outras categorias de ensaio/relato).
SEEDS = [
    "https://www.kitchenbutterfly.com/category/chicken-recipes/",
    "https://www.kitchenbutterfly.com/category/meat-recipes/",
    "https://www.kitchenbutterfly.com/category/fish-and-seafood-recipes/",
    "https://www.kitchenbutterfly.com/category/nigerian-soups-and-global-soups/",
    "https://www.kitchenbutterfly.com/category/stews-sauces/",
    "https://www.kitchenbutterfly.com/category/bean-recipes/",
    "https://www.kitchenbutterfly.com/category/nigerian-jollof-rice-recipes/",
    "https://www.kitchenbutterfly.com/category/plantain-recipes/",
    "https://www.kitchenbutterfly.com/category/salad-recipes/",
    "https://www.kitchenbutterfly.com/category/pasta-recipes/",
    "https://www.kitchenbutterfly.com/category/cookies-cakes/",
    "https://www.kitchenbutterfly.com/category/desserts-sweet-treat-recipes-kitchen-butterfly/",
    "https://www.kitchenbutterfly.com/category/drinks/",
    "https://www.kitchenbutterfly.com/category/homemade-condiments/",
    "https://www.kitchenbutterfly.com/category/nigerian-snacks/",
    "https://www.kitchenbutterfly.com/category/nigerian-breakfast-ideas-morning-recipes-pancake-recipes-kitchen-butterfly/",
]

# Slugs de raiz que NÃO são receitas (navegação, páginas institucionais, hubs).
_NAO_RECEITA = {
    "about", "about-2", "contact", "the-book", "books", "book", "shop",
    "features-press", "press", "favorites-et-al", "my-bucket-list", "blog",
    "all-recipes", "recipes", "how-to", "free-digital-library", "seasonal-produce",
    "nigerian-cuisine", "the-new-nigerian-kitchen", "newsletter", "subscribe",
    "privacy-policy", "terms", "search", "category", "tag", "wprm_print",
    "new-nigerian-christmas", "merry-christmas",
}

# Marcadores de slug que denunciam ensaio/relato (não-receita), mesmo numa categoria de receita.
_RUIDO = (
    "an-exploration", "photo-essay", "book-review", "review-", "reflections",
    "musings", "on-orange-pekoe", "in-the-library", "guest-post",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:  # categorias/paginação têm >1 segmento; receitas são slug de raiz
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(m in slug for m in _RUIDO):
        return False
    # kebab-case (palavras separadas por hífen); exclui ids e slugs com underscore
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite, max_paginas=300)
