"""Adaptador: Chef Tariq (cozinha do Médio Oriente / Palestina) — via sitemap.

WordPress/Yoast: /sitemap.xml → /sitemap_index.xml → post-sitemap.xml. As receitas
ficam SOB /recipe/<slug>/. O mesmo post-sitemap também lista /guides/ (artigos de
técnica/ingrediente) e /lifestyle/ (posts pessoais), que NÃO são receitas — basta exigir
o prefixo /recipe/ para isolar as receitas individuais.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Chef Tariq"
SITE = "cheftariq.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.cheftariq.com"


# Só seguimos o sub-sitemap de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap / author-sitemap (páginas institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs sob /recipe/ que, por garantia, não são receitas individuais.
_NAO_RECEITA = {"recipe", "recipes", "category", "tag", "author"}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # Receita = /recipe/<slug>/  (exatamente 2 segmentos, prefixo "recipe").
    # Exclui /guides/<...>, /lifestyle/<...>, /<pagina-raiz>, taxonomia, etc.
    if len(partes) != 2 or partes[0].lower() != "recipe":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA:
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
