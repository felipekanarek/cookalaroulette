"""Adaptador: Akis Petretzikis (Grécia) — caso de site BLOQUEADO (Cloudflare, HTTP 403).

Estratégia (FR-009): tenta o sitemap via requests; ao bloquear (Cloudflare "Just a
moment..."), cai para o helper genérico `coletar_por_sitemap_browser` (Chromium, corpo
bruto do XML). O sitemap é um único urlset (~14k URLs) que mistura blog e receitas em
grego (raiz) e inglês (/en/). Escolhemos a versão em inglês para títulos legíveis:
receitas individuais ficam em https://akispetretzikis.com/en/recipe/<id>/<slug>.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Akis Petretzikis"
SITE = "akispetretzikis.com"
TECNICAS = ["sitemap", "playwright"]
BASE_URL = "https://akispetretzikis.com"

# Padrão de receita individual (versão inglesa): /en/recipe/<id>/<slug>
_RE_RECEITA = re.compile(r"^/en/recipe/\d+/[^/]+$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    return bool(_RE_RECEITA.match(p.path.rstrip("/")))


def coletar(limite: int) -> list[dict]:
    try:
        return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
    except base.BloqueioError:
        return base.coletar_por_sitemap_browser(BASE_URL, CHEF, SITE, _e_receita, limite)
