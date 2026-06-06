"""Adaptador: David Lebovitz (França) — descoberta via Wayback.

O site está atrás do Cloudflare e responde 403 tanto a requests quanto a Chromium
(headless e headed) — sondagem 2026-06-06. Em vez de contornar a proteção, descobrimos
as URLs de receita pelo Internet Archive (CDX): as URLs são reais (o humano acessa
normalmente no navegador) e o app só precisa da localização para redirecionar.

É um WordPress; as receitas ficam em slug de raiz (https://www.davidlebovitz.com/<slug>/).
Ele publica MUITO post não-receita (viagem, crônica, livros), que compartilham a mesma
forma de URL. O sinal discriminante observado no Wayback: os slugs de receita são
descritivos e contêm o token "recipe" (ou "recette"), ex.: /almond-cake-recipe/,
/banana-ice-cream-recipe/, /quiche-lorraine-recipe-recette/. Posts de viagem/crônica
não têm esse token (ex.: /10-favorite-french-cheeses/, /al-taglio-italian-pizza-paris/).

Filtramos exigindo o token "recipe"/"recette" e excluímos o plural ("recipes" =
roundups/índices) e um punhado de posts meta/promo de livro que mencionam a palavra.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "David Lebovitz"
SITE = "davidlebovitz.com"
TECNICAS = ["wayback"]

# slug em kebab-case puro (sem extensões, sem chars escapados de URL)
_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
# token "recipe" ou "recette" como palavra inteira dentro do slug
_TOKEN = re.compile(r"(?:^|-)(?:recipe|recette)(?:$|-)")

# Slugs que CONTÊM o token mas NÃO são receitas individuais (roundups, índices,
# posts meta sobre receitas, divulgação de livro de receitas).
_NAO_RECEITA = (
    "recipes", "recettes", "guide", "cookbook", "perfect-scoop",
    "drinking-french", "how-precise", "washington-post", "search-online",
    "egg-substitution", "favorite-",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if not _KEBAB.match(slug):
        return False
    if not _TOKEN.search(slug):
        return False
    return not any(d in slug for d in _NAO_RECEITA)


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_wayback(SITE, CHEF, SITE, _e_receita, limite,
                                    cdx_filtro=r".*(recipe|recette).*")
