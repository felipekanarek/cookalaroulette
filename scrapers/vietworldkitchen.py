"""Adaptador: Viet World Kitchen (Andrea Nguyen) — via sitemap.

WordPress/Yoast (sitemap_index.xml → post-sitemap.xml, post-sitemap2.xml). Blog antigo
migrado do TypePad: os posts ficam em /blog/AAAA/MM/<slug>.html e MISTURAM receitas com
artigos (viagem, restaurantes, lançamentos de livro, guias de compra, notícias, resenhas).
Os slugs dos posts de 2007-2009 vêm TRUNCADOS (ex.: "pho-in-oxford-d", "coconut-cake-on"),
o que torna qualquer heurística por "palavra de prato" não confiável.

Filtro adotado (conservador): a Andrea marca as receitas individuais com a palavra
**"recipe"** no slug (singular). Exigimos esse token e excluímos os casos em que ele
aparece em contexto de artigo/listicle (roundups com "recipes" no plural, resenhas,
índices, lançamentos de livro etc.). Isso entrega só páginas de receita real e viva
(~410 no catálogo atual) — coletamos APENAS a URL, nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Andrea Nguyen"
SITE = "vietworldkitchen.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.vietworldkitchen.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap / author-sitemap (páginas institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Token "recipe" SINGULAR (não "recipes"): o plural quase sempre indica listicle/roundup
# ("asian-salmon-recipes", "banh-mi-recipes", "10-recipes-for-...").
_RECEITA_SINGULAR = re.compile(r"\brecipe\b(?!s)")

# Mesmo contendo "recipe", estes marcadores denunciam post NÃO-receita
# (resenha, lançamento/concurso de livro, índice, guia de compra, notícia, evento).
_PADROES_NAO_RECEITA = (
    "review", "giveaway", "winner", "cookbook", "buying-guide", "buyers-guide",
    "history", "interview", "favorite-recipe", "where-to", "how-to-buy",
    "how-to-find", "how-to-order", "what-is", "whats-", "eating-in", "restaurant",
    "-event", "event-", "contest", "kickstarter", "awards", "post-mortem",
    "-news", "news-", "roundup", "sneak-preview", "early-review", "press-event",
    "book-tour", "release-book", "book-trailer", "handbook-review",
    "recipe-index", "recipes-needed", "recipes-wanted", "recipe-contest",
)

# Forma do post: /blog/AAAA/MM/<slug>.html
_FORMA_POST = re.compile(r"^/blog/\d{4}/\d{2}/(?P<slug>[^/]+?)\.html$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    m = _FORMA_POST.match(p.path)
    if not m:
        return False
    slug = m.group("slug").lower()
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # exige a palavra "recipe" (singular) no slug
    return bool(_RECEITA_SINGULAR.search(slug.replace("-", " ")))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
