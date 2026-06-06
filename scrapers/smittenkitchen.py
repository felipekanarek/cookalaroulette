"""Adaptador: Smitten Kitchen (Deb Perelman, EUA) — via sitemap.

WordPress/Yoast, mas com duas particularidades em relação ao caso "slug de raiz"
(ex.: recipetineats):

1) O `/sitemap.xml` NÃO é um índice Yoast com sub-sitemaps de posts; é um único
   `urlset` plano (~1000 locs mais recentes). Logo `sub_filtro` de "post-sitemap"
   não se aplica aqui.
2) As receitas ficam em caminho com data: `/AAAA/MM/<slug>/` (ex.:
   `/2013/07/one-pan-farro-with-tomatoes/`), não em slug de raiz.

Além disso, o robots.txt declara um `Sitemap:` malformado (`http:///sitemap.xml`,
sem host), o que faz `descobrir_sitemaps` devolver uma URL inválida e quebrar o
`coletar_por_sitemap` padrão. Por isso lemos o sitemap conhecido diretamente via
`base.iter_urls_sitemap`, reaproveitando os demais primitivos do base
(fazer_registro / humanizar_slug / registro_valido). Só localização, nunca conteúdo
(Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Deb Perelman"
SITE = "smittenkitchen.com"
TECNICAS = ["sitemap"]
SITEMAP_URL = "https://smittenkitchen.com/sitemap.xml"

# Receita = caminho com data /AAAA/MM/<slug>/. As páginas não-receita do sitemap
# (books, travel, events, podcast, privacy-policy, videos, ...) não têm esse padrão,
# então o próprio formato do caminho já as exclui — dispensa stoplist.
_RECEITA_RE = re.compile(r"^/\d{4}/\d{2}/[a-z0-9]+(?:-[a-z0-9]+)*/?$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    return bool(_RECEITA_RE.match(p.path.lower()))


def coletar(limite: int) -> list[dict]:
    vistos = set()
    registros: list[dict] = []
    for url in base.iter_urls_sitemap(SITEMAP_URL):  # BloqueioError propaga
        if len(registros) >= limite:
            break
        if url in vistos or not _e_receita(url):
            continue
        vistos.add(url)
        r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(url), url)
        if base.registro_valido(r):
            registros.append(r)
    return registros
