"""Adaptador: Punch (US — coquetéis) — via sitemap.

Punch (punchdrink.com) é WordPress/Yoast com sitemap index em /sitemap_index.xml.
O conteúdo é separado por TIPO de post em sitemaps dedicados: article-sitemap*
(matérias), city-guides, hub, glossary, lookbook, venue, region, author... e
recipe-sitemap*.xml — onde ficam as receitas de coquetel.

As "receitas" deste catálogo são drinks/coquetéis (a marca Punch é o "chef"), mas
seguem o mesmo contrato {chef, site, titulo, url}. A URL de receita tem padrão limpo:

    /recipes/<slug>/   -> RECEITA (coquetel)

Basta seguir só os sub-sitemaps `recipe-sitemap` e exigir o caminho /recipes/<slug>,
o que descarta artigos, guias de cidade, glossário, venues, autores e a página de
índice /recipe-archives/. Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Punch"
SITE = "punchdrink.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://punchdrink.com"


# Só seguimos os sub-sitemaps de RECEITAS (recipe-sitemap, recipe-sitemap2, ...),
# evitando article-sitemap / venue / glossary etc. Cuidado para não casar
# "recipe-categories-sitemap" (taxonomia), por isso exigimos "recipe-sitemap".
def _sub_sitemap_de_receitas(url: str) -> bool:
    return "recipe-sitemap" in url.lower()


# URL canônica de receita: /recipes/<slug>/ (exatamente dois segmentos: "recipes" + slug).
def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False  # exclui /recipe-archives/, /recipes/ (índice) e qualquer outro tipo
    slug = partes[1].lower()
    # slug em kebab-case com palavras (evita ids/numéricos puros)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
