"""Adaptador: Yeji's Kitchen Stories (Yeji, Coreia) — via sitemap.

WordPress + All in One SEO: sitemap.xml → post-sitemap.xml. As receitas ficam em slug
de raiz: https://yejiskitchenstories.com/<slug>/ (mesma forma do RecipeTin Eats).
Particularidade: muitos slugs trazem o nome coreano em Hangul
(ex.: /shrimp-stew-freezer-meal-kit-새우탕/), então o filtro aceita letras Unicode,
não só ASCII kebab-case. As <image:loc> do sitemap ficam aninhadas em <image:image>
e NÃO são captadas por iter_urls_sitemap (só lê <loc> direto de <url>).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse, unquote

from . import base

CHEF = "Yeji"
SITE = "yejiskitchenstories.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://yejiskitchenstories.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap / post_tag-sitemap (institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais e guias de presente).
_NAO_RECEITA = {
    "about", "contact", "contact-form", "privacy-policy", "terms", "disclosure",
    "recipes", "recipes-2", "gift-guides", "category", "tag", "author",
    "subscribe", "shop", "search", "newsletter", "faq", "press", "blog",
    "sample-page", "coming-soon",
}

# Padrões em slugs que indicam post não-receita (guias de presente, listas-âncora).
_PADROES_NAO_RECEITA = (
    "gifts-for", "gift-guide",
)

# Slug = palavras separadas por hífen, aceitando letras Unicode (Hangul) e dígitos.
# \w cobre [a-zA-Z0-9_] + letras Unicode; barramos "_" e exigimos pelo menos 2 segmentos
# para evitar tokens isolados (a maioria das receitas tem nome composto).
_SLUG = re.compile(r"^[^\W_]+(?:-[^\W_]+)+$", re.UNICODE)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:  # receita no slug-raiz: /slug/
        return False
    slug = unquote(partes[0]).lower()  # %-decodifica Hangul percent-encoded
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    return bool(_SLUG.match(slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
