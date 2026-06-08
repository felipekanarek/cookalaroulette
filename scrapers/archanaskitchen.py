"""Adaptador: Archana's Kitchen (Archana Doshi) — via sitemap.

Portal indiano enorme (~8000 receitas). O sitemap único (sitemap.xml, urlset plano)
mistura receitas com seções do portal: artigos, vídeos, coleções, planos de refeição,
categorias, cozinhas, tags. As receitas individuais vivem TODAS sob um caminho dedicado:
https://archanaskitchen.com/recipe/<slug>  (exatamente 2 segmentos, sem sub-páginas).

Basta exigir o prefixo /recipe/<slug> para isolar receita de todo o resto do portal.
O sitemap usa o host sem www (archanaskitchen.com); _e_receita normaliza o www.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Archana Doshi"
SITE = "archanaskitchen.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.archanaskitchen.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # Receita individual = /recipe/<slug> (exatamente 2 segmentos). Tudo o mais do portal
    # (articles, collection, meal-plans, category, cuisine, meal-course, tags, search) cai fora.
    if len(partes) != 2 or partes[0].lower() != "recipe":
        return False
    slug = partes[1].lower()
    # slug em kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
