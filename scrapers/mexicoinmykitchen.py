"""Adaptador: Mexico in My Kitchen (Mely Martínez, México) — via sitemap (navegador).

WordPress/Yoast: sitemap_index.xml → post-sitemap.xml (onde ficam as receitas), além de
page-sitemap / category-sitemap (institucional/taxonomia). As receitas ficam em slug de
raiz: https://www.mexicoinmykitchen.com/<slug>/ (mesma forma do RecipeTin Eats).

O site está atrás de Cloudflare (cf-mitigated: challenge → 403 no cliente HTTP comum),
mas o sitemap abre via Chromium pelo CORPO BRUTO da resposta. Por isso usamos
`coletar_por_sitemap_browser`. Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Mely Martínez"
SITE = "mexicoinmykitchen.com"
TECNICAS = ["sitemap", "playwright"]
BASE_URL = "https://www.mexicoinmykitchen.com"


# Só seguimos o sub-sitemap de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap (páginas institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais, índices).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "recipe-index", "category", "tag", "author", "subscribe",
    "shop", "cookbook", "my-account", "web-stories", "search", "newsletter",
    "faq", "press", "blog", "es", "advertise", "work-with-me", "media",
    "instapage", "links",
}

# Padrões em slugs que indicam roundup/listicle (coletânea de várias receitas),
# não uma receita individual.
_PADROES_NAO_RECEITA = (
    "-recipes",          # ex.: shredded-chicken-recipes, mexican-tacos-recipes
    "recipes-with-",     # ex.: recipes-with-poblano-peppers
    "recipes-using-",    # ex.: cocktail-recipes-using-tequila
    "game-day",
    "party-food-ideas",
    "buffet-table",
    "giveaway", "winner", "review", "guide-to", "menu",
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
    return base.coletar_por_sitemap_browser(BASE_URL, CHEF, SITE, _e_receita, limite,
                                            sub_filtro=_sub_sitemap_de_posts)
