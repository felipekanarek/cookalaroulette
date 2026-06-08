"""Adaptador: Paola Carosella (paolacarosella.com.br) — via sitemap.

Site WordPress + Yoast: o sitemap_index.xml aponta para sub-sitemaps; as receitas vivem
em https://paolacarosella.com.br/receitas/<slug>/ e estão listadas no `post-sitemap.xml`
(e também no `wprm_recipe-sitemap.xml`, que porém inclui o placeholder /receitas/receita/).
Seguimos só o post-sitemap, evitando page/category/author-sitemap (institucional/taxonomia).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Paola Carosella"
SITE = "paolacarosella.com.br"
TECNICAS = ["sitemap"]
BASE_URL = "https://paolacarosella.com.br"


# Só seguimos o sub-sitemap de POSTS (onde estão as receitas), evitando
# page-sitemap / category-sitemap / author-sitemap (páginas institucionais e taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs sob /receitas/ que NÃO são receitas individuais (placeholder do WP Recipe Maker
# e eventuais páginas de índice/arquivo).
_NAO_RECEITA = {"receita", "receitas"}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # estrutura exata: /receitas/<slug>/
    if len(partes) != 2 or partes[0] != "receitas":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA:
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
