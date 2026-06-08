"""Adaptador: Minimalist Baker (Dana Shulman) — via crawl BFS.

WordPress/Yoast, mas o sitemap_index.xml lista sub-sitemaps (post-sitemap*.xml) que
respondem 500/520 a qualquer cliente que não seja o Googlebot (bloqueio Cloudflare
específico dos sub-sitemaps) — inclusive via navegador. O site público, porém, é
totalmente acessível por HTTP comum. Por isso descobrimos as receitas por crawl BFS a
partir das páginas de índice (/recipe-index/, /recipes/), que listam receitas e revelam
mais receitas via "relacionadas".

As receitas ficam em slug de raiz: https://minimalistbaker.com/<slug>/ (mesma forma do
RecipeTin Eats). Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Dana Shulman"
SITE = "minimalistbaker.com"
TECNICAS = ["crawl"]

# Páginas-semente: índices que listam muitas receitas (e linkam para mais).
SEEDS = [
    "https://minimalistbaker.com/recipe-index/",
    "https://minimalistbaker.com/recipes/",
]

# Slugs de raiz que NÃO são receitas (institucionais, taxonomia, utilitários).
_NAO_RECEITA = {
    "about", "contact", "privacy-policy", "terms", "disclosure", "disclaimer",
    "recipes", "recipe-index", "category", "tag", "author", "everyday-cooking",
    "comments", "feed", "shop", "subscribe", "newsletter", "search", "faq",
    "press", "media", "advertise", "work-with-me", "resources", "my-account",
    "web-stories", "cart", "checkout", "blog", "cookbook", "cookbooks",
    "favorites", "food-photography-resources", "how-to", "start-here",
}

# Padrões em slugs que indicam roundup/listicle (coletânea de receitas), não receita
# individual. Ex.: "best-vegan-memorial-day-recipes", "easy-valentines-day-desserts",
# "recipes-for-coffee-lovers", "gluten-free-mothers-day-desserts".
_PADROES_NAO_RECEITA = (
    "recipes", "best-", "favorite-", "roundup", "gift-guide", "-guide",
    "game-day-snacks", "desserts", "-treats-for-", "-lovers",
)


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
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite, max_paginas=40)
