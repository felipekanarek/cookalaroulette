"""Adaptador: Cecilia Tupac (Peru) — via sitemap.

Site Wix com sitemap-index limpo via requests (sem 403). As receitas ficam no blog,
em https://www.ceciliatupac.com/post/<slug>, e o sub-sitemap de posts
(blog-posts-sitemap.xml) lista todas. O blog mistura receitas com alguns artigos
("roundups" de receitas e textos editoriais), filtrados por padrão de slug abaixo.

Os slugs são em espanhol e contêm acentos (ñ, á, í...), então o predicado aceita
caracteres acentuados — diferente dos exemplos kebab-case ASCII.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse, unquote

from . import base

CHEF = "Cecilia Tupac"
SITE = "ceciliatupac.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.ceciliatupac.com"


# Só seguimos o sub-sitemap de POSTS do blog (onde ficam as receitas), evitando
# event-pages / store-products / pages (institucionais, loja, eventos).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "blog-posts-sitemap" in url.lower()


# Posts que NÃO são receitas individuais: "roundups" (listas de receitas) e artigos
# editoriais. Detectados por marcadores no slug.
_PADROES_NAO_RECEITA = (
    r"^\d+-recetas",            # "6-recetas-...", "5-recetas-peruanas-de-pollo"
    r"^\d+-superalimentos",     # "5-superalimentos-peruanos-..."
    r"recetas-tradicionales",   # roundups de tradição
    r"recetas-peruanas",        # roundups genéricos
    r"d[oó]nde-",               # "dónde-encontrar...", "dónde-comprar..."
    r"d[oó]nde-comprar",
    r"en-el-reino-unido",       # artigos sobre o Reino Unido
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receitas: /post/<slug>
    if len(partes) != 2 or partes[0] != "post":
        return False
    slug = unquote(partes[1]).lower()
    if not slug:
        return False
    for padrao in _PADROES_NAO_RECEITA:
        if re.search(padrao, slug):
            return False
    return True


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
