"""Adaptador: Made With Lau (Daddy Lau) — culinária cantonesa/chinesa, via sitemap.

Site moderno (Next.js, Vercel), mas o sitemap.xml é servido por HTTP comum (200, XML),
sem precisar de navegador. As receitas ficam em /recipes/<slug>; o restante do sitemap é
institucional (/family, /collections, /authors/*) ou a própria listagem (/recipes).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Daddy Lau"
SITE = "madewithlau.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.madewithlau.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente dois segmentos: /recipes/<slug>  (exclui /recipes, /collections, /authors/x)
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 2 or partes[0] != "recipes":
        return False
    slug = partes[1].lower()
    # slug kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
