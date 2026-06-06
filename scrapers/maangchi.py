"""Adaptador: Maangchi — caso de site BLOQUEADO (anti-bot, HTTP 403).

Estratégia (FR-009): tenta sitemap via requests; se bloquear, usa o helper genérico
`coletar_por_sitemap_browser` (Chromium, corpo bruto, recursa índice). Receitas em
https://www.maangchi.com/recipe/<slug>.
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Maangchi"
SITE = "maangchi.com"
TECNICAS = ["sitemap", "playwright"]
BASE_URL = "https://www.maangchi.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "maangchi.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    return len(partes) == 2 and partes[0] == "recipe"


def coletar(limite: int) -> list[dict]:
    try:
        return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
    except base.BloqueioError:
        return base.coletar_por_sitemap_browser(BASE_URL, CHEF, SITE, _e_receita, limite)
