"""Adaptador: Souped Up Recipes (Mandy) — via sitemap.

Site de culinária chinesa hospedado no WordPress.com (Jetpack). O sitemap-index é
/sitemap.xml → /sitemap-1.xml (urlset único e plano). As receitas ficam em slug de
raiz: https://soupeduprecipes.com/<slug>/ (mesma forma do RecipeTin Eats).

Além de páginas institucionais e da loja (/shop/...), Mandy publica posts de
utensílios/wok (reviews de panela, faca, etc.) que NÃO são receitas — excluídos pelo
filtro abaixo.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Mandy"
SITE = "soupeduprecipes.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://soupeduprecipes.com"


# O índice (/sitemap.xml) lista sitemap-N.xml (páginas/posts), image-sitemap-*.xml e
# video-sitemap-*.xml. Só seguimos os de PÁGINAS: os de imagem trazem posts-anexo
# (placeholder-image, wok-icon, ...) que não são receitas.
def _sub_sitemap_de_paginas(url: str) -> bool:
    nome = url.rsplit("/", 1)[-1].lower()
    return bool(re.match(r"^sitemap-\d+\.xml$", nome))


# Slugs de raiz que NÃO são receitas (institucionais, loja, taxonomia).
_NAO_RECEITA = {
    "contact", "recipe-archive", "recommended-products", "shop", "cart",
    "my-account", "privacy-policy", "souped-up-recipe-privacy-policy",
    "terms", "about", "about-me", "newsletter", "subscribe", "search",
    "category", "tag", "author", "page", "checkout", "wishlist",
}

# Padrões em slugs que indicam post não-receita (review de utensílio, guia, etc.).
_PADROES_NAO_RECEITA = (
    "carbon-steel-wok", "flat-bottom-wok", "wok-for-", "-wok-set",
    "knife-set", "review", "recommended-product",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # apenas slug de raiz (/slug/); descarta /shop/... e demais multi-segmento
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_paginas)
