"""Adaptador: Linda Lomelino (Call me cupcake!, Suécia) — via sitemap.

Blog de confeitaria sueco em WordPress. O robots.txt aponta o sitemap core do WP
(wp-sitemap.xml); as receitas são posts no padrão Blogger-style de raiz:
https://www.callmecupcake.se/<ano>/<mes>/<slug>.html (slug em inglês ou sueco).

Sitemap limpo → coletar_por_sitemap, seguindo apenas o sub-sitemap de POSTS
(wp-sitemap-posts-post-*) e descartando page/taxonomies/users. Alguns posts não são
receita (workshops, fotografia, viagens, lançamentos de livro, artesanato DIY); o
predicado os filtra por palavras-chave no slug. Título = slug humanizado (sem .html).
Só localização, nunca conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Linda Lomelino"
SITE = "callmecupcake.se"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.callmecupcake.se"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / taxonomies / users (páginas institucionais, taxonomia, autores).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "posts-post" in url.lower()


# Marcadores de slug que indicam post NÃO-receita (workshops, fotografia, viagem,
# livros, artesanato DIY). Mantém receitas mesmo quando trazem "how-to" (ex.: massa
# de torta, focaccia art), filtrando só o que claramente não é comida.
_NAO_RECEITA_KWS = (
    "workshop", "photography", "styling", "travel", "guide-to",
    "giveaway", "win-my-book", "my-new-book", "second-book", "new-book",
    "book-teaser", "interview", "behind-the-scenes", "diy-", "-diy",
    "paper-stars", "paper-bows", "yarn-hat", "floating-cloud", "garland",
    "ornament", "announcement", "lamps",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "callmecupcake.se" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # padrão real dos posts: /AAAA/MM/slug.html
    if len(partes) != 3:
        return False
    ano, mes, arquivo = partes
    if not (re.match(r"^\d{4}$", ano) and re.match(r"^\d{2}$", mes)):
        return False
    if not arquivo.lower().endswith(".html"):
        return False
    slug = arquivo[:-5].lower()  # remove .html
    if not slug:
        return False
    if any(kw in slug for kw in _NAO_RECEITA_KWS):
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
