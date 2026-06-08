"""Adaptador: Sonia Peronaci (Itália) — via sitemap.

WordPress/Yoast: sitemap_index.xml lista um sitemap dedicado de receitas
(custom post type): sp-recipe-sitemap.xml / sp-recipe-sitemap2.xml (~1500 receitas).
As receitas ficam em slug de raiz: https://www.soniaperonaci.it/<slug>/

Como há sitemap exclusivo de receitas, basta seguir só esses sub-sitemaps
(sub_filtro) e validar a forma do slug — posts/páginas/categorias ficam de fora.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Sonia Peronaci"
SITE = "soniaperonaci.it"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.soniaperonaci.it"


# Só seguimos os sub-sitemaps de RECEITAS (custom post type sp_recipe),
# ignorando post-/page-/category-/sp-list-sitemap (blog, institucionais, taxonomia).
def _sub_sitemap_de_receitas(url: str) -> bool:
    return "sp-recipe-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (defesa extra, caso algo escape do sitemap).
_NAO_RECEITA = {
    "about", "chi-sono", "contatti", "contact", "privacy-policy", "cookie-policy",
    "termini", "ricette", "category", "categoria", "tag", "author", "autore",
    "shop", "negozio", "search", "cerca", "newsletter", "faq", "press", "blog",
    "es", "en", "home", "corsi", "libri", "video",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # receita no slug-raiz: /slug/  ou  /slug
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    # slug em kebab-case (palavras separadas por hífen); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
