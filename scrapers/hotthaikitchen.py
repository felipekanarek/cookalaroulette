"""Adaptador: Hot Thai Kitchen (Pailin Chongchitnant, Tailândia) — descoberta via Wayback.

O site (https://hot-thai-kitchen.com, SEM www) está atrás do desafio JS da Cloudflare
("Just a moment..."), que devolve 403 ao cliente HTTP comum E não passa no Chromium
headless. Em vez de contornar a proteção, descobrimos as URLs de receita pelo Internet
Archive (CDX) — as URLs são reais e o humano acessa normalmente no navegador.

É WordPress: as receitas ficam em slug de raiz, https://hot-thai-kitchen.com/<slug>/,
kebab-case (ex.: /chicken-adobo/, /pad-thai-1/, /beef-rendang/). O CDX, porém, devolve
muito ruído no mesmo nível de raiz que precisamos descartar:
  - páginas institucionais / taxonomia (about, contact, recipes, category, subscribe…);
  - junk técnico do WP/plugins (geocode, marker-listing, rest-api, 404, load, player…);
  - páginas de anexo/thumbnail que ESPELHAM receitas reais (sufixo -mini / -mini-N / -sm,
    ou "title-page"): /pad-thai-mini/ duplica /pad-thai-1/ — descartadas;
  - conteúdo de viagem/vlog/festival (vlog, -fest, day-trip, interview, food-market…);
  - guias de ingrediente "-101" e roundups "N-recipes/things/ways/tips/top-N".
O filtro abaixo mantém só receitas individuais (~600 slugs reais no arquivo).
Só localização (URL), nunca conteúdo.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Pailin Chongchitnant"
SITE = "hot-thai-kitchen.com"
TECNICAS = ["wayback"]


# Slugs de raiz que NÃO são receitas (institucional / taxonomia / junk de WP e plugins).
_NAO_RECEITA = {
    "about", "about-pailin", "contact", "privacy-policy", "terms", "recipes",
    "recipe", "category", "categories", "tag", "tags", "subscribe", "shop",
    "store", "cookbook", "cookbooks", "books", "book", "my-account", "cart",
    "checkout", "search", "newsletter", "faq", "press", "blog", "videos",
    "video", "episodes", "ingredients", "ingredient", "glossary", "events",
    "media", "patreon", "membership", "members", "gift", "web-stories",
    # junk técnico do WordPress / plugins observado no CDX
    "404", "load", "player", "geocode", "geocode-cache", "marker-listing",
    "rest-api", "system-health-tools", "performance-tools", "page-recipes",
    "recipe-video", "htk-cook", "cool-stuff", "ama-1", "map", "map-2",
    "ask-pai", "directions", "coconut-milk-doc", "thai-house",
    "equipment-for-thai-cooking", "rice-cooker-comparison",
    "accessibility", "autocomplete", "all-recipes-by-categories",
    "asian-store-guide", "ama-1-2", "bangkok-market", "banana-r",
    "base64", "behind-the-scenes", "behind-the-scenes-thai-restaurants",
    "best-p", "best-wok-to-buy",
}

# Sufixos/fragmentos que marcam anexo de imagem (espelham receitas reais) ou conteúdo
# editorial não-receita (viagem, vlog, merch, guias). Aplicado por busca no slug.
_FRAGMENTOS_RUIDO = (
    "vlog", "-fest", "day-trip", "interview", "heritage", "food-market",
    "floating-market", "chatuchak", "-tour", "-museum", "bizarre",
    "presentation-", "htk-merch", "htk-tshirt", "title-page",
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
    # kebab-case com palavras; rejeita ids/numéricos puros e caracteres estranhos
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        return False
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    # anexos/thumbnails que duplicam receitas reais: -mini, -mini-N, -sm
    if re.search(r"-(?:mini(?:-\d+)?|sm)$", slug):
        return False
    # guias de ingrediente ("fish-sauce-101", "lemongrass-101")
    if slug.endswith("-101"):
        return False
    # roundups / listicles começando por número ("10-recipes-for-...",
    # "5-ways-...", "5-tips-...", "4-thai-leftover-recipes", "top-5-..."); NÃO confundir
    # com receitas tipo "5-min-pad-thai" / "30-min-crispy-pork-belly".
    if re.match(r"^\d+-", slug) and (
        "recipes" in slug or re.match(r"^\d+-(?:things|ways|tips)\b", slug)
    ):
        return False
    # páginas de utilidade no nível de raiz: guias, faqs (ex.: "agar-agar-faq")
    if slug.endswith("-faq") or slug.endswith("-guide"):
        return False
    if re.match(r"^top-\d+\b", slug):
        return False
    if any(frag in slug for frag in _FRAGMENTOS_RUIDO):
        return False
    return True


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_wayback(SITE, CHEF, SITE, _e_receita, limite)
