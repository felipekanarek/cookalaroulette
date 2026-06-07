"""Adaptador: Vincenzo's Plate (Vincenzo Prosperi, Itália) — via crawl BFS.

É WordPress (Yoast), com receitas no slug-raiz: https://www.vincenzosplate.com/<slug>/.
O post-sitemap (562 posts) mistura receitas com muito conteúdo não-receita: vídeos de
"taste test", posts de viagem (pescara-beach, abruzzo-italy), listas (top-10-...), e-book,
etc. — poluindo o slug-raiz. Em vez do sitemap, partimos das páginas de listagem
(/recipe-items/ e /recipes/) e seguimos os links de receita que cada página revela
(BFS), trafegando só por páginas de receita real e filtrando o ruído conhecido.

Coleta APENAS localização (chef/site/titulo/url) — nunca conteúdo. Python 3.9.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Vincenzo Prosperi"
SITE = "vincenzosplate.com"
TECNICAS = ["crawl"]
SEEDS = [
    "https://www.vincenzosplate.com/recipe-items/",
    "https://www.vincenzosplate.com/recipes/",
]

# Slugs-raiz que NÃO são receitas (páginas institucionais, listagem, taxonomia, loja).
_NAO_RECEITA = {
    "recipes", "recipe-items", "category", "filter", "tag", "author", "about",
    "contact", "privacy-policy", "terms", "shop", "say-ciao", "chef-vincenzo",
    "italian-tour", "authentic-italian-cookbook", "authentic-italian-cook-book",
    "my-account", "cart", "checkout", "subscribe", "newsletter", "blog", "search",
    "press", "media", "video", "videos", "page", "feed", "amp",
}

# Marcadores de conteúdo não-receita embutidos no slug (vídeos de degustação, tours, e-book).
_MARCADORES_RUIDO = ("taste-test", "tour", "cookbook", "-test", "blindfolded", "blind-")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # receitas ficam em slug de raiz: exatamente um segmento de caminho
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(m in slug for m in _MARCADORES_RUIDO):
        return False
    # kebab-case com pelo menos duas palavras (evita páginas de uma palavra/genéricas)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)+$", slug))


def coletar(limite: int) -> list[dict]:
    # Crawl BFS tolerante a 429 (devolve o parcial já coletado). Sob a carga do lote o
    # site rate-limita as páginas de receita internas; o crawl ainda entrega o que reuniu
    # antes do bloqueio. Se vier vazio (semente bloqueada já de cara), cai para a listagem
    # via navegador, que passa pelo rate-limit e extrai as receitas das páginas de índice.
    try:
        registros = base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite)
    except base.BloqueioError:
        registros = []
    if registros:
        return registros
    return base.coletar_por_listagem(SEEDS, CHEF, SITE, _e_receita, limite, usar_browser=True)
