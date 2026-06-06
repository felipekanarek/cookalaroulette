"""Adaptador: Bela Gil (Brasil) — via sitemap (WordPress core).

O site usa o sitemap nativo do WordPress (wp-sitemap.xml), com um custom post type
dedicado a receitas. As receitas reais ficam em:
    https://belagil.com/conteudo/receitas/<slug>/
(slug em kebab-case → título limpo via humanizar_slug).

Há também um post type `receitas_dia_a_dia` (/conteudo/receitas-dia-a-dia/<data-slug>/),
mas seus slugs têm prefixo de data (ex.: 2018-8-23-...) que polui o título derivado;
por isso coletamos apenas o catálogo principal `/conteudo/receitas/`.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Bela Gil"
SITE = "belagil.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://belagil.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "belagil.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # /conteudo/receitas/<slug>
    if len(partes) != 3 or partes[0] != "conteudo" or partes[1] != "receitas":
        return False
    slug = partes[2].lower()
    if slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
