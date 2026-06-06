"""Adaptador: Flavia Imperatore (Misya) — Itália — via sitemap.

O índice de sitemap (https://www.misya.info/sitemap.xml) é acessível por requests comum.
As receitas ficam em https://www.misya.info/ricetta/<slug>.htm ("ricetta" = receita em
italiano) e estão concentradas nos sub-sitemaps post-sitemap*.xml. Os demais sub-sitemaps
(category, tag, ingrediente, page, etc.) trazem taxonomia/páginas institucionais, então só
seguimos os de posts. Coleta apenas localização (chef/site/titulo/url), nunca conteúdo.
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Flavia Imperatore (Misya)"
SITE = "misya.info"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.misya.info"


# Receitas vivem nos sub-sitemaps de posts (post-sitemap.xml, post-sitemap2.xml, ...).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "misya.info" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # padrão real: /ricetta/<slug>.htm
    return len(partes) == 2 and partes[0] == "ricetta" and partes[1].endswith(".htm")


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
