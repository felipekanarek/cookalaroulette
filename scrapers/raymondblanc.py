"""Adaptador: Raymond Blanc (França/Reino Unido) — via sitemap.

Site em Vercel com sitemap único e plano (sem índice aninhado) em
https://raymondblanc.com/sitemap.xml. As receitas ficam sob /recipes/<slug>/.
O sitemap também lista restaurante, hotel, cursos, livros e páginas
institucionais — tudo isso é excluído pelo filtro, que aceita só /recipes/<slug>/.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Raymond Blanc"
SITE = "raymondblanc.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://raymondblanc.com"

# Primeiro segmento /recipes/ que NÃO é uma receita individual (índice, taxonomia).
_NAO_RECEITA = {"", "category", "tag", "page", "all", "index"}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # exige exatamente /recipes/<slug>  → exclui /recipes/ (índice) e o resto do site
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
