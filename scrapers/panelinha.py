"""Adaptador: Panelinha (Rita Lobo) — site SEM sitemap → crawl BFS.

Não há sitemap, e a listagem (/receitas) é uma SPA que não carrega dados por XHR. Mas as
páginas de receita são server-rendered e expõem ~11 links de "receitas relacionadas".
Então partimos da homepage (6 receitas em destaque) e seguimos os links relacionados de
página em página (`coletar_por_crawl`), descobrindo o catálogo em largura.
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Rita Lobo"
SITE = "panelinha.com.br"
TECNICAS = ["crawl"]
SEEDS = ["https://www.panelinha.com.br/"]


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "panelinha.com.br" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    return len(partes) == 2 and partes[0] == "receita"


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite)
