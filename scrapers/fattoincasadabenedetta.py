"""Adaptador: Fatto in Casa da Benedetta (Benedetta Rossi, Itália) — sitemap via navegador.

WordPress/Yoast com vários sitemaps tipados em /sitemap_index.xml. As receitas têm
sitemaps DEDICADOS: recipe-sitemap.xml, recipe-sitemap2.xml ... recipe-sitemap6.xml, e
ficam em /ricetta/<slug>/. O site fica atrás de Cloudflare (challenge para cliente HTTP
comum → 403), mas o Chromium passa: por isso coletamos os sitemaps via navegador
(coletar_por_sitemap_browser, que lê o CORPO bruto do XML).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Benedetta Rossi"
SITE = "fattoincasadabenedetta.it"
TECNICAS = ["sitemap", "playwright"]
BASE_URL = "https://www.fattoincasadabenedetta.it"


# Só seguimos os sub-sitemaps de RECEITAS (recipe-sitemap*.xml), evitando
# post/page/collection/advice/book/course e os sitemaps de taxonomia (diet, time,
# difficulty-level, course, season, etc.) — nenhum é receita individual.
def _sub_sitemap_de_receitas(url: str) -> bool:
    return "recipe-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # Receita individual: /ricetta/<slug>/  (exatamente 2 segmentos).
    # Exclui o índice bare /ricetta/ (1 segmento) e qualquer aninhamento extra.
    if len(partes) != 2 or partes[0].lower() != "ricetta":
        return False
    slug = partes[1].lower()
    if slug.isdigit():
        return False
    # slug em kebab-case (palavras com hífen); evita ids/numéricos puros e lixo.
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap_browser(BASE_URL, CHEF, SITE, _e_receita, limite,
                                            sub_filtro=_sub_sitemap_de_receitas)
