"""Adaptador: Downshiftology (Lisa Bryan, EUA) — via sitemap.

WordPress/Yoast: sitemap_index.xml → recipes-sitemap.xml (sitemap dedicado às receitas).
As receitas ficam em https://downshiftology.com/recipes/<slug>/. Há também um
post-sitemap.xml, mas ele é só conteúdo de estilo de vida/viagem (não-receita), então
seguimos APENAS o recipes-sitemap via sub_filtro.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Lisa Bryan"
SITE = "downshiftology.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://downshiftology.com"


# Só seguimos o sitemap dedicado de receitas; ignora post/page/category/author/video.
def _sub_sitemap_de_receitas(url: str) -> bool:
    return "recipes-sitemap" in url.lower()


# Slugs sob /recipes/ que NÃO são receita individual (índice/taxonomia).
_NAO_RECEITA = {
    "category", "tag", "page", "course", "cuisine", "method", "diet",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # exatamente /recipes/<slug>/ (2 segmentos); exclui o índice /recipes/
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA:
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
