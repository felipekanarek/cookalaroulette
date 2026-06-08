"""Adaptador: My Colombian Recipes (Erica Dinho) — via sitemap.

WordPress/Yoast: sitemap_index.xml → post-sitemap*.xml. As receitas ficam em slug de
raiz: https://www.mycolombianrecipes.com/<slug>/ (mesma forma do RecipeTin Eats).
Há também variantes em espanhol sob /es/<slug>/, que também são receitas.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Erica Dinho"
SITE = "mycolombianrecipes.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.mycolombianrecipes.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap (páginas institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (posts de viagem, institucionais, sorteios).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "category", "tag", "author", "subscribe", "shop", "cookbook",
    "my-account", "web-stories", "search", "newsletter", "faq", "press",
    "blog", "es", "advertise", "work-with-me", "media",
    "welcome-to-the-new-site", "about-colombia", "colombian-fruits",
    "this-is-medellin", "cartagena-de-indias",
}

# Padrões em slugs que indicam post não-receita (viagem, sorteio, evento, notícia).
_PADROES_NAO_RECEITA = (
    "giveaway", "the-penol-rock", "guatape", "winner", "review",
    "virtual-event", "cookbook-news", "pre-orders", "brunch-menu",
    "menu", "travel", "guide-to", "my-trip", "about-",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # /slug/  (1 segmento) ou /es/slug/  (variante em espanhol, 2 segmentos)
    if len(partes) == 1:
        slug = partes[0].lower()
    elif len(partes) == 2 and partes[0].lower() == "es":
        slug = partes[1].lower()
    else:
        return False
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
