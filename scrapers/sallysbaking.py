"""Adaptador: Sally's Baking Addiction (Sally McKenney, EUA) — via wayback.

O site (WordPress) está totalmente atrás de Cloudflare: tanto /sitemap.xml quanto
/robots.txt e as próprias páginas devolvem 403 com `cf-mitigated: challenge` ao cliente
HTTP (e ao Chromium headless). Como só precisamos da URL para redirecionar (Princípio III),
descobrimos as receitas pelo Internet Archive (CDX), sem tocar no site.

As receitas ficam em slug de raiz: https://sallysbakingaddiction.com/<slug>/
(mesma forma de RecipeTin Eats / My Colombian Recipes). O CDX devolve também ruído sob cada
receita (/comment-page-N/, /feed/, /print/, /print-recipe/), variantes ?query e fragmentos
URL-encoded — todos eliminados por `_e_receita` (a wayback já remove query/fragmento e
normaliza http→https). Restam ainda posts não-receita (roundups "N-recipes-for-...",
dicas de blog, listas de utensílios), filtrados por `_PADROES_NAO_RECEITA`.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Sally McKenney"
SITE = "sallysbakingaddiction.com"
TECNICAS = ["wayback"]

# Padrões em slugs que indicam post não-receita: roundups/listas, dicas de blog,
# utensílios, retrospectivas, sorteios, bastidores.
_PADROES_NAO_RECEITA = (
    "tips-for-", "-tips-", "tips-on-", "growing-your-food-blog", "food-blog",
    "-tools", "kitchen-tools", "baking-tools", "recipe-superlatives",
    "recipes-for", "-recipes", "baking-basics", "giveaway", "behind-the",
    "how-to-grow", "favorite-things", "gift-guide", "my-trip", "-roundup",
    "best-of-", "week-in", "currently-", "ask-sally", "q-and-a",
)

# Slugs exatos que NÃO são receitas (institucionais/seções).
_NAO_RECEITA = {
    "about", "about-sally", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "recipe-index", "category", "tag", "author", "subscribe", "shop",
    "cookbook", "cookbooks", "my-account", "web-stories", "search", "newsletter",
    "faq", "press", "blog", "advertise", "work-with-me", "media", "sallys-cookie-palooza",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    # netloc pode vir com :80 (capturas antigas do archive) — normaliza.
    host = p.netloc.replace("www.", "").split(":")[0]
    if host != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:  # receita é slug de raiz: /slug/  (exclui /slug/feed, /slug/print, datas)
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    if slug.isdigit():  # arquivos por ano (/2012/, /2013/) e ids
        return False
    # kebab-case com ≥2 palavras (evita slug de palavra única, taxonomia e lixo URL-encoded)
    return bool(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_wayback(SITE, CHEF, SITE, _e_receita, limite)
