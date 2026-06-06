"""Adaptador: Serious Eats (Kenji López-Alt e equipe) — descoberta via Wayback.

O site está atrás do Cloudflare (bloqueia requests E Chromium headless). Em vez de
contornar a proteção, descobrimos as URLs de receita pelo Internet Archive (CDX) — as URLs
são reais e o humano acessa normalmente no navegador. Padrão de receita: slug de raiz
terminando em id numérico e contendo "recipe", ex.: /the-best-chili-recipe-5118930.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Kenji López-Alt / Serious Eats"
SITE = "seriouseats.com"
TECNICAS = ["wayback"]

_RECEITA = re.compile(r"^/[a-z0-9-]+-\d{5,}$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "seriouseats.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    return bool(_RECEITA.match(p.path.rstrip("/"))) and "recipe" in partes[0]


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_wayback(SITE, CHEF, SITE, _e_receita, limite,
                                    cdx_filtro=r".*-recipe-[0-9]{5,}.*")
