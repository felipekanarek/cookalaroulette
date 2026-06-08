"""Adaptador: Chocolate & Zucchini (Clotilde Dusoulier) — via sitemap.

Blog clássico (WordPress/Yoast) que MISTURA receitas com colunas, ensaios, viagens,
entrevistas e coletâneas. O sitemap raiz é /sitemap_index.xml (robots.txt aponta lá);
os posts vivem em /post-sitemap.xml e /post-sitemap2.xml — é onde estão TODAS as receitas,
ao lado de muito conteúdo não-receita.

A URL carrega a seção no caminho, num padrão limpo:

    /recipes/<categoria>/<slug>-recipe/   -> RECEITA individual   (~524 posts)
    /nopic/<slug>-recipe/                  -> RECEITA sem foto      (raro, mas válido)
    /essays/...  /paris/...  /travels/...  /ingredients-fine-foods/...
    /interviews/...  /books-cookbooks/...  /links/...  /series/...   -> artigo/coluna (excluído)

Filtro: só aceitamos caminho sob /recipes/ (ou /nopic/) cujo último segmento termine em
`-recipe` (ou `-recipe-N`). Isso já descarta:
  - ensaios que casualmente têm "recipe" no slug (ex.: /essays/happiness-a-recipe/), pois
    exigimos o prefixo /recipes/;
  - "how-to", "best-tips", "on-fresh-peas" etc. (não terminam em -recipe);
  - a categoria /recipes/round-ups/ (coletâneas, não receita individual), excluída à mão
    porque há 1 coletânea que termina em -recipe (holiday-recipes-recipe).

Coleta APENAS a URL — nunca o conteúdo (Princípio III). Título derivado do slug.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Clotilde Dusoulier"
SITE = "cnz.to"
TECNICAS = ["sitemap"]
BASE_URL = "https://cnz.to"

# Categorias sob /recipes/ que são coletâneas/listas, não receita individual.
_NAO_RECEITA_CATS = {"round-ups"}

# Último segmento de receita: termina em -recipe ou -recipe-<n>.
_SLUG_RECEITA_RE = re.compile(r"-recipe(?:-\d+)?$")


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page/attachment/book/product/category/tag-sitemap (institucional e taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if not partes:
        return False
    # Seção raiz precisa ser /recipes/ (com categoria) ou /nopic/.
    if partes[0] == "recipes":
        if len(partes) < 3:            # /recipes/ ou /recipes/<cat>/ não são receita
            return False
        if partes[1] in _NAO_RECEITA_CATS:
            return False
    elif partes[0] == "nopic":
        if len(partes) < 2:
            return False
    else:
        return False
    return bool(_SLUG_RECEITA_RE.search(partes[-1]))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
