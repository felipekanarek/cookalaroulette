"""Adaptador: King Arthur Baking (marca, EUA) — via sitemap.

Marca editorial (Drupal + módulo Simple XML Sitemap): o sitemap.xml é um índice
paginado (/sitemap.xml?page=1..N) servido por HTTP comum (200), sem precisar de
navegador. As receitas ficam em /recipes/<slug> (slug único, geralmente terminando
em "-recipe"); o restante são blog, vídeos, podcast, autores, loja/produtos e páginas
institucionais — além de hubs sob /recipes/ (collections, features, resources/...)
que NÃO são receitas individuais.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "King Arthur Baking"
SITE = "kingarthurbaking.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.kingarthurbaking.com"

# Segmentos sob /recipes/ que são hubs/categorias, não receitas individuais.
_NAO_RECEITA = {"collections", "features", "resources", "category", "search"}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente dois segmentos: /recipes/<slug>
    # (exclui /recipes, /recipes/resources/..., loja/produtos, blog, videos, etc.)
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 2 or partes[0] != "recipes":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA:
        return False
    # slug kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
