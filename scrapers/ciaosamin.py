"""Adaptador: Ciao Samin (Samin Nosrat) — via sitemap.

Site Framer (estático, não-WordPress): /sitemap.xml lista tudo num único urlset.
As receitas ficam sob /recipes/<slug> (exatamente 2 segmentos). Excluímos:
- /recipes/categories/...  (taxonomia, 3+ segmentos)
- /shop/...                (loja)
- /about, /appearances, / (institucional / raiz)
Acervo pequeno (~27 receitas), típico de uma chef autoral.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Samin Nosrat"
SITE = "ciaosamin.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://ciaosamin.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita = exatamente /recipes/<slug>
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False
    slug = partes[1].lower()
    # exclui a taxonomia (/recipes/categories/...) e listagens genéricas
    if slug in {"categories", "all"}:
        return False
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
