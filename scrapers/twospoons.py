"""Adaptador: Two Spoons (Hannah Sunderani, Canadá) — via sitemap.

WordPress/Yoast: sitemap_index.xml → post-sitemap.xml. As receitas ficam em slug de
raiz: https://www.twospoons.ca/<slug>/ (mesma forma do RecipeTin Eats).

O post-sitemap mistura receitas com não-receitas: reviews de produto, guias de viagem
("vegan-guide-to-..."), roundups ("N-best-...-recipes", listas de receitas), e posts de
estilo de vida (skincare, IVF). O filtro abaixo remove esses ruídos por slug/padrão.
Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Hannah Sunderani"
SITE = "twospoons.ca"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.twospoons.ca"


# Só seguimos o sub-sitemap de POSTS (onde ficam as receitas), evitando page/category/
# season/special-diet/web-story-sitemap (páginas institucionais e taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais, blog, taxonomia).
_NAO_RECEITA = {
    "blog", "about", "about-me", "contact", "privacy-policy", "terms",
    "disclosure", "recipes", "category", "tag", "author", "subscribe",
    "shop", "cookbook", "my-account", "web-stories", "search", "newsletter",
    "faq", "press", "work-with-me", "media", "fall-favourites",
}

# Padrões em slugs que indicam post não-receita: review de produto, guia de viagem,
# roundup/lista de receitas, post de estilo de vida.
_PADROES_NAO_RECEITA = (
    "review",            # review-chirp-body-hair-mask, gruvi-review, ...
    "guide-to",          # vegan-guide-to-vienna / paris / porto / marrakech
    "ivf",               # my-ivf-success-story
    "skincare",          # skincare-tips-for-healthy-glowing-skin
    "where-to-eat",
    "places-to-eat",
    "things-to-do",
    "challenge",         # the-7-day-smoothie-bowl-challenge-day-5
    "how-to-store",      # how-to-store-vegetables (guia, não receita)
    "how-to-cut",        # how-to-cut-a-butternut-squash (técnica, não receita)
    "pantry",            # easy-pantry-recipes (lista)
    "wherefore-art-thou",
)

# Roundups: slugs que são LISTAS de receitas (plural "recipes" no fim, ou contagem no
# começo "21-best-...", "25-best-..."). Receita individual usa singular "recipe".
_RE_ROUNDUP_RECIPES = re.compile(r"-recipes$")
_RE_CONTAGEM_INICIAL = re.compile(r"^\d+-")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:                       # receita no slug-raiz: /slug/
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    if _RE_ROUNDUP_RECIPES.search(slug) or _RE_CONTAGEM_INICIAL.match(slug):
        return False
    # slug com palavras (kebab-case, ≥2 palavras); evita slugs de 1 token (páginas soltas)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)+$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
