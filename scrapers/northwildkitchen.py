"""Adaptador: Nevada Berg (North Wild Kitchen, Noruega) — via crawl BFS a partir de /recipe/.

O site é Yoast/WordPress com receitas em slug de raiz (https://northwildkitchen.com/<slug>/),
mas o post-sitemap mistura receitas com posts de viagem, fazenda, festivais e estilo de vida
(ex.: "moose-hunting-elgjakten", "ona-crab-fishing", "numedal-matfestival") — slug-raiz poluído.
Por isso partimos das listagens /recipe/ e /recipe-index/ (que só linkam receitas reais) e
seguimos os links de receita que cada página revela ("receitas relacionadas"), descobrindo o
catálogo em largura sem trafegar pelos posts não-culinários.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Nevada Berg"
SITE = "northwildkitchen.com"
TECNICAS = ["crawl"]
SEEDS = [
    "https://northwildkitchen.com/recipe/",
    "https://northwildkitchen.com/recipe-index/",
]

# Slugs de raiz que NÃO são receitas (páginas institucionais/seções vistas no crawl).
_NAO_RECEITA = {
    "home", "recipe", "recipe-index", "blog", "about", "about-nevada-berg",
    "about-north-wild-kitchen", "contact", "privacy-policy", "cookbook",
    "video-channel", "the-farm", "shop", "newsletter", "search", "press",
    "winter", "spring", "summer", "autumn", "fall",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "northwildkitchen.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if slug.startswith("about-"):  # páginas "sobre" diversas
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case (exclui underscore)


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite)
