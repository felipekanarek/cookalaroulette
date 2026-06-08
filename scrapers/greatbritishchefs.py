"""Adaptador: Great British Chefs (marca editorial, UK) — via sitemap.

O CHEF é a MARCA "Great British Chefs": o site é editorial e agrega receitas de
centenas de chefs britânicos sob uma curadoria única. /sitemap.xml é um único urlset
(~7 MB, 200 OK, sem Cloudflare) com tudo do site. As receitas ficam em slug de raiz
sob /recipes/<slug> (sempre UM segmento depois de "recipes"). O sitemap também traz
features/, collections/, how-to-cook/, contributors/, chefs/, restaurants/, etc. —
o filtro abaixo restringe à página de receita individual.

Coleta APENAS a URL (localização), nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Great British Chefs"
SITE = "greatbritishchefs.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.greatbritishchefs.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    if "//" in p.path:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita individual = exatamente /recipes/<slug> (dois segmentos).
    # Exclui chefs/, ingredients/, features/, collections/, campaigns/,
    # how-to-cook/, contributors/, restaurants/, etc. (segmento inicial != "recipes")
    # e também a listagem /recipes (1 segmento) e categorias mais profundas.
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False
    slug = partes[1].lower()
    # slug em kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
