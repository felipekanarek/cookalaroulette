"""Adaptador: Nigella Lawson (Reino Unido) — site CUSTOM (não-WordPress), via sitemap.

Sondagem do site (junho/2026):
- Não há /robots.txt (404), mas /sitemap.xml é um único <urlset> (~5.7 MB, ~27 mil URLs)
  acessível pelo cliente HTTP comum (sem 403).
- As receitas da própria Nigella ficam em https://www.nigella.com/recipes/<slug>
  (profundidade 2). Ex.: /recipes/african-drumsticks.
- Profundidade 3 separa coleções que NÃO são receitas autorais da Nigella:
  /recipes/members/<slug> (receitas da comunidade), /recipes/guests/<slug> (convidados)
  e /recipes/branded/<slug> (conteúdo patrocinado). Excluímos essas para manter a
  atribuição ao chef honesta.
- Slugs reservados de listagem em profundidade 2 (members/guests/branded/search) também
  são descartados.

Coleta APENAS a localização (chef/site/titulo/url) — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Nigella Lawson"
SITE = "nigella.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.nigella.com"

# Segmentos de listagem/coleção sob /recipes/ que não são receitas individuais.
_NAO_RECEITA = {"members", "guests", "branded", "search"}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # exatamente /recipes/<slug> (receitas autorais da Nigella); profundidade 3
    # (members/guests/branded) fica de fora.
    if len(partes) != 2 or partes[0] != "recipes":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
