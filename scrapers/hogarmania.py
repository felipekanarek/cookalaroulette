"""Adaptador: Karlos Arguiñano (Espanha) — via sitemap (sub_filtro de seção).

hogarmania.com é um portal grande (cozinha, lar, jardim, decoração, bricolagem,
mascotes, beleza...). As receitas de cozinha do Karlos Arguiñano ficam SÓ na seção
`/cocina/recetas/` e têm sitemaps próprios.

O /sitemap.xml padrão dá 403 (CloudFront), mas o robots.txt aponta o índice real:
`/hogarmania_sitemap_index.xml`, que lista sitemaps por seção. Seguimos APENAS os
4 sitemaps de receitas (primeros, segundos, postres, otros) via `sub_filtro`, e
`_e_receita` restringe ao path `/cocina/recetas/...html` — excluindo artigos de
cozinha (escuela-cocina, alimentos, consejos, actualidad) e todo o resto do portal
(hogar, jardineria, decoracion, bricolaje, mascotas, belleza, tareas).

Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Karlos Arguiñano"
SITE = "hogarmania.com"
TECNICAS = ["sitemap"]
# robots.txt aponta o índice real (o /sitemap.xml padrão dá 403 na CDN).
BASE_URL = "https://www.hogarmania.com/hogarmania_sitemap_index.xml"

# Só seguimos os sub-sitemaps de RECEITAS DE COZINHA (excluindo articulos_cocina,
# articulos_hogar/jardineria/decoracion/bricolaje/mascotas/belleza, tareas, authors,
# portadas, google_news).
_SITEMAPS_RECEITAS = ("recetas_primeros", "recetas_segundos", "recetas_postres",
                      "recetas_otros")


def _sub_sitemap_de_receitas(url: str) -> bool:
    u = url.lower()
    return any(chave in u for chave in _SITEMAPS_RECEITAS)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # Receita = página individual sob a seção de cozinha, terminando em .html.
    # Ex.: /cocina/recetas/ensalada-cobb.html
    #      /cocina/recetas/postres/flan-de-queso-de-cabra.html
    # Exclui artigos (/cocina/escuela-cocina/, /cocina/alimentos/, ...) e o resto
    # do portal (jardineria, decoracion, etc.).
    if not p.path.startswith("/cocina/recetas/"):
        return False
    if not p.path.lower().endswith(".html"):
        return False
    # Precisa de um slug real após /cocina/recetas/ (não a própria seção/índice).
    resto = p.path[len("/cocina/recetas/"):]
    return bool(re.search(r"[a-z0-9]", resto, re.IGNORECASE))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
