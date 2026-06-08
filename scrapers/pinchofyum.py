"""Adaptador: Pinch of Yum (Lindsay Ostrom) — via sitemap.

WordPress/Yoast: sitemap_index.xml → post-sitemap*.xml. As receitas ficam em slug de
raiz: https://pinchofyum.com/<slug> (sem barra final, 1 segmento).

Pinch of Yum começou como blog pessoal/de blogging, então o post-sitemap mistura
muita coisa que NÃO é receita: roundups/listicles ("10 easy recipes...", "favorite
X recipes"), relatórios de renda (income reports), posts sobre fotografia de comida,
blogging e lifestyle. O filtro abaixo remove esses padrões; o slug de receita
individual é kebab-case e descreve um prato.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Lindsay Ostrom"
SITE = "pinchofyum.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://pinchofyum.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap / web-story-sitemap / video-sitemap.
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais, recursos do blog, navegação).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "recipe", "category", "tag", "author", "subscribe", "shop",
    "cookbook", "cookbooks", "my-account", "web-stories", "search", "newsletter",
    "faq", "press", "blog", "advertise", "work-with-me", "media", "resources",
    "start-here", "income-reports", "food-blogger-pro", "tasty-food-photography",
    "sponsor", "portfolio", "team", "amazon-shop", "gift-guide",
}

# Substrings em slugs que indicam post NÃO-receita: roundups/listicles, lifestyle,
# blogging, fotografia de comida, relatórios de renda, viagem, etc.
_PADROES_NAO_RECEITA = (
    "-recipes",          # roundups: "12-favorite-instant-pot-soup-recipes", "easy-dinner-recipes"
    "-ideas",            # "breakfast-ideas"
    "-dishes",           # "10-last-minute-thanksgiving-side-dishes" (roundups de pratos)
    "ways-to",           # "12-creative-ways-to-use-kitchenaid-mixer"
    "must-try", "must-bake", "must-make",
    "round-up", "roundup",
    "income-report", "traffic-income", "making-money",
    "food-photography", "food-photos", "photography-workshop",
    "full-time-blogging", "blog-while", "blogger-burnout", "blogging",
    "food-blogger-pro",
    "gift-guide", "etsy-favorites", "capsule-wardrobe", "summer-wardrobe",
    "day-in-this-life", "day-in-the-life", "a-day-in", "life-at-the",
    "things-love-this-friday", "things-i-bought", "things-i-love",
    "vacation", "to-montana", "of-alaska", "our-trip", "my-trip", "summit",
    "behind-the", "meet-our", "our-life", "our-first-ever",
    "what-you-should-know", "everything-you-need-to-know",
    "favorite-",         # "favorite-lentil-recipes", "favorite-mexican-crockpot-recipes"
    "how-to-start", "how-many-hours", "how-to-eat-more",
    "open-enrollment", "launch-day", "save-the-date", "come-have-a-look",
    "workshop", "bloggers-and-books", "food-blogs",
    # diário/pessoal (Pinch of Yum começou como blog de vida, 2010-2012)
    "quarantine-report", "coffee-date", "lunch-date", "highlight-reel",
    "the-hardest", "guess-what", "now-what", "getting-over-it",
    "said-and-done", "little-things", "small-victories", "scenes-from",
    "home-for-the-year", "young-and-wild", "places-etc", "dinner-club",
    "thoughts-at", "tiny-bloom", "introducing-sage", "sage-in-", "partyparty",
    "japanese-halloween", "instagram-playbook", "bank-robbery",
    "evolution-of-a-food-photo", "holiday-survival-guide", "slow-fall-rhythm",
    "in-october", "in-may", "in-august", "this-friday",
)

# Slug numérico-listicle: começa com "N-" seguido de roundup. Números puros de tempo
# de preparo ("10-minute-...", "15-minute-...") SÃO receitas, então só barramos quando
# o resto sugere coletânea (tratado por _PADROES_NAO_RECEITA acima via "-recipes" etc.).
_LISTICLE = re.compile(r"^\d{1,3}-(?!minute\b)(?:easy|best|fresh|favorite|must|things|ways|creative|cozy|healthy|delicious|simple|amazing|quick|last-minute|meals|days|miles|reasons)")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:                       # receita = exatamente 1 segmento
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    if _LISTICLE.match(slug):
        return False
    # kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
