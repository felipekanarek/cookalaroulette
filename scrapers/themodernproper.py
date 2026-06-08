"""Adaptador: The Modern Proper (Holly Erickson & Natalie Mortimer, EUA) — via sitemap.

As receitas ficam em slug de raiz: https://themodernproper.com/<slug>
O sitemap raiz (/sitemap.xml → /sitemaps-1-sitemap.xml) é um índice por "section". As
receitas vivem nos sub-sitemaps da seção `postEntries` (paginados p1..pN); as demais seções
(about, contact, homepage, newsletter, cookbook) são institucionais.

Dentro de postEntries há também posts de coletânea/listas ("17-best-summer-grilling-recipes",
"23-best-easter-dinner-recipes...") — não são receitas individuais e ficam de fora. As páginas
"how-to-..." são receitas de prato único (mantidas).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "The Modern Proper"
SITE = "themodernproper.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://themodernproper.com"


# No índice de sitemaps, só seguimos os sub-sitemaps da seção postEntries (receitas/posts);
# ignora about/contact/homepage/newsletter/cookbook. O índice raiz (.xml) sempre passa.
def _sub_sitemap_de_posts(url: str) -> bool:
    low = url.lower()
    if "section-postentries" in low:
        return True
    # deixa o índice raiz recursar; barra os outros urlset de seção
    return "-section-" not in low


# Slugs de raiz que NÃO são receitas (institucionais / taxonomia).
_NAO_RECEITA = {
    "about", "contact", "newsletter", "cookbook", "homepage", "recipes",
    "blog", "category", "tag", "search", "privacy", "terms", "shop",
    "subscribe", "press", "faq",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento de caminho: /slug
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    # slug em kebab-case; evita ids numéricos puros
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug) or slug.isdigit():
        return False
    # coletâneas/listas começam com número ("17-best-...", "23-easter-...") — não são
    # receitas individuais.
    if re.match(r"^\d+-", slug):
        return False
    return True


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
