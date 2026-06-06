"""Adaptador: Trine Hahnemann (Dinamarca) — via sitemap.

O site é WordPress com sitemap core (wp-sitemap.xml) que expõe um post-type dedicado
de receitas: wp-sitemap-posts-recipe-1.xml. As receitas ficam em
https://trinehahnemann.com/recipe/<slug>/ — todas em inglês (sem versão dinamarquesa
paralela no domínio), então não há risco de duplicação por idioma.
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Trine Hahnemann"
SITE = "trinehahnemann.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://trinehahnemann.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "trinehahnemann.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    return len(partes) == 2 and partes[0] == "recipe"


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
