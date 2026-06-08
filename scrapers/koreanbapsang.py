"""Adaptador: Korean Bapsang (Hyosun Ro) — via sitemap.

WordPress/Yoast (Cloudflare na frente, mas o sitemap_index.xml e os sub-sitemaps são
servidos ao cliente HTTP comum). As receitas ficam em slug de raiz:
https://www.koreanbapsang.com/<slug>/ (mesma forma do RecipeTin Eats / My Colombian Recipes).
O post-sitemap também traz posts de coletânea ("15 Korean Soup Recipes"), viagem
("Trip to Korea") e institucionais — filtrados em _e_receita.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Hyosun"
SITE = "koreanbapsang.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.koreanbapsang.com"


# Só seguimos o sub-sitemap de POSTS (onde ficam as receitas), evitando
# page-sitemap / web-story-sitemap / category-sitemap (institucional, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais, índices).
_NAO_RECEITA = {
    "about", "contact", "privacy-policy", "terms", "disclosure",
    "all-recipes", "ingredients", "featured-on", "start-here",
    "category", "tag", "author", "subscribe", "shop", "cookbook",
    "my-account", "web-stories", "search", "newsletter", "faq", "press",
    "korean-pantry-seasoning-ingredients", "menus-korean-dinner-parties",
}

# Padrões em slugs que indicam post de coletânea/viagem/evento (não-receita individual).
_PADROES_NAO_RECEITA = (
    "-recipes",          # "15-easy-kimchi-recipes", "spring-vegetable-recipes"
    "trip-korea",        # diários de viagem
    "drama-food",        # "korean-drama-food-itaewon-class"
    "super-bowl",        # coletâneas temáticas
    "that-use-",         # "15-recipes-that-use-gochujang"
    "back-to-school",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento de caminho: /slug/  ou  /slug
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    # coletâneas começam com número ("15-...", "20-...") → não é receita individual
    if re.match(r"^\d+-", slug):
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
