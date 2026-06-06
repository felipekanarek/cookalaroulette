"""Adaptador: Jamie Oliver — via sitemap.

As receitas ficam sob https://www.jamieoliver.com/recipes/<categoria>/<slug>/
(ex.: /recipes/pasta-recipes/spaghetti-carbonara/). Excluímos a raiz /recipes/ e
páginas de categoria (que têm apenas 1 segmento após /recipes/).
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Jamie Oliver"
SITE = "jamieoliver.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.jamieoliver.com"

# Receitas ficam em /recipes/<categoria>/<slug>/. O primeiro segmento costuma ser um
# ingrediente/tipo (vegetables, chicken, pasta...). Estes segmentos são TAXONOMIA
# (páginas de coleção), não receitas individuais:
_TAXONOMIA = {
    "books", "dishtype", "course", "occasion", "cuisine", "special-diets",
    "cooking-method", "budget", "nutrition", "category", "tag", "christmas",
    "halloween", "easter", "mothers-day", "fathers-day", "valentines-day",
    "ingredients", "tv", "method", "features", "family", "world", "news",
    "family-favourites", "budget-friendly-hub", "budget-friendly", "hub",
    "quick-and-easy-recipes", "healthy-recipes", "baking-recipes-hub",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "jamieoliver.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # exatamente: recipes / <categoria> / <slug>
    if len(partes) != 3 or partes[0] != "recipes":
        return False
    return partes[1] not in _TAXONOMIA


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
