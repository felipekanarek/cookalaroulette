"""Adaptador: Zoe Adjonyoh (Gana / Zoe's Ghana Kitchen) — via sitemap.

RESSALVA IMPORTANTE (sondado em 2026-06): o domínio do briefing `zoesghana.com`
NÃO resolve (NXDOMAIN). O site real da chef é `zoeadjonyoh.com`, mas hoje ele é
apenas uma página de venda de domínio (GoDaddy "parking-lander"): todas as rotas
respondem com um stub que redireciona para `/lander`, e o sitemap.xml lista apenas
`/lander`. Não há receitas vivas a coletar — `coletar()` retorna [] por ora.

Mantemos a técnica de SITEMAP porque é a abordagem correta caso o site volte ao ar
como blog (WordPress/estático). O predicado `_e_receita` descarta a página de
parking e slugs institucionais; se o catálogo voltar, a coleta passa a funcionar
sem alterações. Coleta APENAS localização (chef/site/titulo/url), nunca conteúdo.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Zoe Adjonyoh"
SITE = "zoeadjonyoh.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://zoeadjonyoh.com"

# Slugs que NUNCA são receita: a landing de venda do domínio e páginas institucionais.
_NAO_RECEITA = {
    "lander", "recipes", "recipe", "blog", "about", "about-zoe", "contact",
    "shop", "books", "book", "cookbook", "press", "events", "newsletter",
    "subscribe", "search", "privacy-policy", "terms", "faq", "cart", "account",
    "supper-club", "supper-clubs", "restaurant", "menu", "home", "category",
    "tag", "author",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if SITE not in p.netloc.replace("www.", ""):
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:  # receita esperada em slug de raiz: /<slug>
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case


def coletar(limite: int) -> list[dict]:
    # O robots.txt deste domínio anuncia "Sitemap: /sitemap.xml" (caminho RELATIVO),
    # o que faz descobrir_sitemaps()/requests quebrar. Iteramos o sitemap real
    # diretamente (URL absoluta) — robusto a esse caso e ao site voltar como blog.
    vistos = set()
    registros: list[dict] = []
    try:
        for url in base.iter_urls_sitemap(base.urljoin(BASE_URL, "/sitemap.xml")):
            if len(registros) >= limite:
                break
            if url in vistos or not _e_receita(url):
                continue
            vistos.add(url)
            r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(url), url)
            if base.registro_valido(r):
                registros.append(r)
    except base.BloqueioError:
        return base.coletar_por_sitemap_browser(BASE_URL, CHEF, SITE, _e_receita, limite)
    return registros
