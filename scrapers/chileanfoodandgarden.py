"""Adaptador: Pilar Hernandez / Chilean Food & Garden (Chile) — via Wayback.

WordPress (Genesis) com receitas em slug de raiz: https://www.chileanfoodandgarden.com/<slug>/.
O site está totalmente atrás de Cloudflare (managed challenge "Just a moment..." mesmo no
/sitemap.xml e /robots.txt — JS obrigatório), então o cliente HTTP e o navegador headless não
passam. Usamos o Internet Archive (CDX) para DESCOBRIR as URLs reais; o app só precisa da
localização para redirecionar (403 da Cloudflare = página viva, FR/Princípio III).

Filtro: receita = slug de raiz em kebab-case (≥2 palavras), excluindo categorias/tags
de uma palavra (appetizers, desserts, beef...), páginas institucionais e arquivos.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Pilar Hernandez"
SITE = "chileanfoodandgarden.com"
TECNICAS = ["wayback"]

# Slugs de raiz que NÃO são receitas individuais: institucionais e categorias/tags
# (taxonomia WordPress que vive em slug de raiz neste tema).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy", "privacy-policy", "licensing",
    "terms", "feed", "author", "category", "tag", "search", "page", "shop",
    "recipes", "recipe-index", "subscribe", "newsletter", "2x",
    # categorias de uma/duas palavras que aparecem como slug de raiz:
    "appetizers", "desserts", "entrees", "salads", "sandwiches", "soups",
    "vegetables", "breakfast", "beef", "chicken", "pork", "fish", "shellfish",
    "pasta", "rice", "potatoes", "bread", "candy", "chocolate", "cookies",
    "cupcakes", "pies", "scones",
}

# Slugs institucionais/taxonomia/lixo (prefixo).
_SLUG_PROIBIDO = re.compile(
    r"^(category|tag|author|page|feed|wp-|cdn-cgi|comments)", re.IGNORECASE
)

# "Food & Garden": metade do site é jardinagem/viagem/lifestyle, que NÃO são receitas
# mas vivem no mesmo slug de raiz. Estes termos (palavra inteira) denunciam essas páginas:
# jardinagem ("grow ... in houston", "garden", "seeds"), viagem/restaurante ("eat denver",
# "carnival cruise"), resenhas e roundups de categoria ("chilean desserts", "cakes bakes").
_TERMOS_NAO_RECEITA = (
    r"garden|gardens|gardening|grow|growing|seeds|seed|plant|planting|compost|"
    r"harvest|harvey|hurricane|kindergarten|backyard|poppies|butterfly|edible|"
    r"book-review|review|book|"
    r"eat-austin|eat-denver|eat-pucon|eat-colorado|travel|cruise|carnival|horizon|"
    r"all-inclusive|things-to|visit|tips|ideas|guide|menus|menu|favorites|"
    r"comfort-food|must-try|7-must|dreams-come-true|get-help"
)
_REGEX_NAO_RECEITA = re.compile(
    r"(?:^|-)(?:" + _TERMOS_NAO_RECEITA + r")(?:-|$)", re.IGNORECASE
)

# Roundups/índices de categoria que viraram slug de raiz (não são uma receita única).
_ROUNDUP = {
    "chilean-recipes", "chiean-recipes", "chilean-desserts", "chilean-salads",
    "chilean-sandwiches", "chilean-vegetables", "chilean-seafood", "chilean-meat",
    "chilean-poultry", "chilean-breakfast", "chilean-bread", "chilean-once",
    "chilean-cakes-bakes", "chilean-cookies-candy", "chilean-jams-jellies",
    "chilean-pasta-rice-potatoes", "chilean-soups-starters", "chilean-peppers-and-chiles",
    "chilean-appetizers-beverages", "chilean-seafood", "cakes-bakes", "cookies-truffles",
    "chilean-recipe", "houston-gardening",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:                      # receita = slug de raiz único: /slug/
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug in _ROUNDUP or slug.isdigit():
        return False
    if "." in slug:                           # arquivos: .txt .xml .js .php .ico
        return False
    if _SLUG_PROIBIDO.match(slug):
        return False
    if _REGEX_NAO_RECEITA.search(slug):       # jardinagem/viagem/lifestyle/resenhas
        return False
    if any(ord(c) > 127 for c in slug) or "%" in slug:   # ?p=, %E2%80%99 etc.
        return False
    # kebab-case com ≥2 palavras (ex.: chilean-ceviche, apple-strudel); descarta
    # slugs de palavra única (ambíguos: viram categorias) e ids tipo "11604-2".
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)+$", slug):
        return False
    if re.match(r"^\d+(?:-\d+)*$", slug):     # "11604-2" = id de post, não receita
        return False
    return True


def coletar(limite: int) -> list[dict]:
    # Site sob Cloudflare total → descoberta via Internet Archive (sem tocar no site).
    return base.coletar_por_wayback(SITE, CHEF, SITE, _e_receita, limite)
