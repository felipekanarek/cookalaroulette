"""Adaptador: Zaatar & Zaytoun (Yosra Hamden, Líbano) — via sitemap.

WordPress/Yoast, mas o índice fica em /sitemap_index.xml (e NÃO em /sitemap.xml,
que dá 404; robots.txt não declara Sitemap:). Por isso não usamos
`descobrir_sitemaps` (que só tenta robots + /sitemap.xml): semeamos o índice
conhecido e seguimos apenas o post-sitemap, onde ficam as receitas.

As receitas ficam em slug de raiz: https://zaatarandzaytoun.com/<slug>/
(domínio canônico SEM www). Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Yosra Hamden"
SITE = "zaatarandzaytoun.com"
TECNICAS = ["sitemap"]
SITEMAP_INDEX = "https://zaatarandzaytoun.com/sitemap_index.xml"


# Só seguimos o sub-sitemap de POSTS (receitas), evitando page-/category-sitemap
# (páginas institucionais e taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas individuais: institucionais/taxonomia e
# posts de "roundup" (coletâneas/listas de receitas, não uma receita).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "category", "tag", "author", "subscribe", "shop", "cookbook",
    "my-account", "web-stories", "search", "newsletter", "faq", "press", "blog",
    "lebanese-manakish-recipes", "vegan-lebanese-recipes", "easy_lebanese_recipes",
    "3-lebanese-recipes-for-beginners",
}

# Padrões em slugs que indicam coletânea/lista (não uma receita única).
_PADROES_NAO_RECEITA = ("-recipes", "_recipes", "recipes-for")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento de caminho: /slug/ ou /slug
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # kebab/snake-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    # O índice canônico não é /sitemap.xml — semeamos sitemap_index.xml e
    # filtramos só o post-sitemap (mesma lógica de coletar_por_sitemap).
    vistos = set()
    registros: list[dict] = []
    for url in base.iter_urls_sitemap(SITEMAP_INDEX, sub_filtro=_sub_sitemap_de_posts):
        if len(registros) >= limite:
            break
        if url in vistos or not _e_receita(url):
            continue
        vistos.add(url)
        r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(url), url)
        if base.registro_valido(r):
            registros.append(r)
    return registros
