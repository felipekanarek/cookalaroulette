"""Adaptador: Damn Delicious (Chung-Ah Rhee) — via sitemap servido pelo navegador.

WordPress/Yoast: sitemap.xml → post-sitemap.xml / post-sitemap2.xml. As receitas usam
permalink baseado em data: https://damndelicious.net/<ANO>/<MES>/<DIA>/<slug>/ (4 segmentos).

O site fica atrás de Cloudflare (cf-mitigated: challenge → 403 no cliente HTTP comum),
mas o Chromium headless recebe o XML cru (resp.text(), status 200). Por isso usamos
coletar_por_sitemap_browser. Coletamos APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Chung-Ah Rhee"
SITE = "damndelicious.net"
TECNICAS = ["sitemap", "playwright"]
BASE_URL = "https://damndelicious.net"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap / video-sitemap (institucional, taxonomia, vídeos).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs (último segmento) que NÃO são receita individual: institucional, taxonomia.
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "recipe-index", "category", "tag", "author", "subscribe", "shop",
    "cookbook", "my-account", "web-stories", "search", "newsletter", "faq",
    "press", "blog", "advertise", "work-with-me", "media", "portfolio",
}

# Padrões no slug que indicam roundup/listicle ou post não-receita (não é receita única).
_PADROES_NAO_RECEITA = (
    "giveaway", "winner", "review", "best-of", "favorite", "gift-guide",
    "holiday-gift", "must-have", "round-up", "roundup", "recipes-for",
    "best-recipes", "easy-recipes", "weeknight", "menu", "meal-plan",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # permalink de data: /ANO/MES/DIA/slug/  → exatamente 4 segmentos
    if len(partes) != 4:
        return False
    ano, mes, dia, slug = partes
    if not (ano.isdigit() and len(ano) == 4 and mes.isdigit() and dia.isdigit()):
        return False
    slug = slug.lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # roundups/listicles começam com número ("10-best-...", "12-quick-...", "8-healthier-...")
    if re.match(r"^\d+[-]", slug):
        return False
    # slug em kebab-case com palavras; evita numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap_browser(BASE_URL, CHEF, SITE, _e_receita, limite,
                                            sub_filtro=_sub_sitemap_de_posts)
