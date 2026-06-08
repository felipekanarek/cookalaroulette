"""Adaptador: Love and Lemons (Jeanine Donofrio) — via sitemap.

WordPress (Google Sitemap Generator): /sitemap.xml → post-sitemap.xml + post-sitemap2.xml.
As receitas ficam em slug de raiz: https://www.loveandlemons.com/<slug>/
(mesma forma do RecipeTin Eats). O blog mistura, nesses mesmos post-sitemaps, posts
não-receita: roundups ("...-ideas", "best-..."), guias de viagem/produto ("...-guide"),
gift guides, sorteios, lançamentos de livro e institucionais — filtrados em `_e_receita`.
País: EUA.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Jeanine Donofrio"
SITE = "loveandlemons.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.loveandlemons.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / misc / externals (páginas institucionais, taxonomia, externos).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais, marca, parcerias).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "recipe-index", "category", "tag", "author", "subscribe",
    "shop", "cookbook", "cookbooks", "my-account", "web-stories", "search",
    "newsletter", "faq", "press", "blog", "media", "advertise", "work-with-me",
    "instagram", "weekend", "daily-harvest", "podcast", "wellness",
}

# Padrões em slugs que indicam post não-receita: roundups, guias, sorteios,
# gift guides, lançamentos/eventos de livro, viagem, reviews de produto.
_PADROES_NAO_RECEITA = (
    "-ideas", "ideas-", "-guide", "guide-", "guide-to", "giveaway",
    "cookbook", "workshop", "-party", "roundup", "round-up", "review",
    "launch", "announc", "sneak", "gift-guide", "gifts-", "-gifts",
    "-trip", "travel", "best-of", "black-friday", "recap", "sale",
    "ultimate-guide", "where-to", "favorite-", "-favorites", "things-to",
    "best-baking", "best-kitchen", "best-mandoline", "best-tofu-press",
    "best-matcha", "best-vegetarian-cookbook",
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
    # posts datados (gift guides anuais etc.) e galerias começam com ano
    if re.match(r"^(19|20)\d{2}", slug):
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros e arquivos wp-*
    if slug.startswith("wp-"):
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
