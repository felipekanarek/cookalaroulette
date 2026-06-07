"""Adaptador: Pati Jinich (México) — via listagem renderizada por navegador.

O post-sitemap mistura receitas com muitas aparições na mídia (cbs/kcrw/npr/...), poluindo
o resultado, então não serve. A página /recipes/ lista receitas reais, mas hoje é renderizada
por JavaScript (o HTML cru não traz nenhum link), então o crawl estático não acha nada.
Solução: renderizamos /recipes/ com Playwright e extraímos os links de receita do DOM.
Limitação conhecida: a listagem carrega só a primeira leva (~12) sem rolagem/"load more";
para mais seria preciso dirigir o scroll no navegador (melhoria futura).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Pati Jinich"
SITE = "patijinich.com"
TECNICAS = ["listagem-navegador"]
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
    return base.coletar_por_listagem(SEEDS, CHEF, SITE, _e_receita, limite, usar_browser=True)
