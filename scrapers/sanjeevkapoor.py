"""Adaptador: Sanjeev Kapoor (Índia) — via crawl BFS a partir de /Recipe.

O site é custom (NÃO-WordPress). Tem sitemap, mas os sitemaps são por DATA
(sitemap_AAAA-MM-DD.xml) e listam só o conteúdo publicado naquele dia — sobretudo
artigos, quase nenhuma receita — então não servem para varrer o catálogo.

As receitas vivem em https://www.sanjeevkapoor.com/Recipe/<slug>-<id> (id numérico).
A página /Recipe e as listagens por curso/cozinha expõem links de receita, e cada
página de receita aponta para "receitas relacionadas" — então partimos dessas
sementes e descobrimos o catálogo em largura (BFS), como em patijinich.

O slug das receitas termina no id numérico (ex.: omelette-11927128); para o título
removemos esse id, derivando o nome legível só da localização (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Sanjeev Kapoor"
SITE = "sanjeevkapoor.com"
TECNICAS = ["crawl"]

SEEDS = [
    "https://www.sanjeevkapoor.com/Recipe",
    "https://www.sanjeevkapoor.com/course/main-course-vegetarian",
    "https://www.sanjeevkapoor.com/course/main-course-chicken",
    "https://www.sanjeevkapoor.com/course/snacks-and-starters",
    "https://www.sanjeevkapoor.com/course/desserts",
]

# /Recipe/<slug>-<id> — id numérico no fim é a marca de receita individual.
_RE_RECEITA = re.compile(r"/Recipe/[a-z0-9].*-\d+$", re.IGNORECASE)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "sanjeevkapoor.com" not in p.netloc:
        return False
    return bool(_RE_RECEITA.search(p.path.rstrip("/")))


def _titulo(url: str) -> str:
    """Nome legível: último segmento do caminho sem o id numérico final."""
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    slug = re.sub(r"-\d+$", "", slug)              # remove o id
    slug = re.sub(r"[-_]+", " ", slug).strip()
    return slug.title() if slug else base.humanizar_slug(url)


def coletar(limite: int) -> list[dict]:
    # coletar_por_crawl faz o BFS e respeita o limite; só refinamos o título
    # (o slug do site carrega o id numérico, que não queremos no rótulo).
    registros = base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite, max_paginas=300)
    for r in registros:
        r["titulo"] = _titulo(r["url"])
    return registros
