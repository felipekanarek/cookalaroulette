"""Adaptador: Yotam Ottolenghi (Reino Unido) — via crawl BFS a partir de receitas.

ottolenghi.co.uk é uma loja Shopify: o mesmo domínio serve produtos (/products/,
/collections/) e páginas institucionais. As receitas individuais ficam em
https://ottolenghi.co.uk/pages/recipes/<slug> (o segmento /pages/recipes/ é a "raiz"
de receita; /pages/recipes — sem slug — é só a página índice de categorias).

O sitemap NÃO lista as receitas individuais (só ~80 páginas de categoria, ex.:
/pages/chicken-recipes), e as páginas de categoria renderizam os cards de receita via
JS (invisíveis ao cliente HTTP). Porém cada PÁGINA DE RECEITA, buscada por HTTP simples
(sem 403), traz links de "receitas relacionadas" para outras /pages/recipes/<slug>.
Por isso usamos crawl BFS: partimos de algumas receitas-semente e seguimos os
relacionados, descobrindo o catálogo em largura. Só localização, nunca conteúdo.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Yotam Ottolenghi"
SITE = "ottolenghi.co.uk"
TECNICAS = ["crawl"]

# Receitas-semente (páginas de receita reais, alcançáveis por HTTP simples). A partir
# delas o BFS segue os "relacionados" e cobre o restante do catálogo.
SEEDS = [
    "https://ottolenghi.co.uk/pages/recipes/southern-fried-chicken",
    "https://ottolenghi.co.uk/pages/recipes/chicken-shawarma-sandwiches",
    "https://ottolenghi.co.uk/pages/recipes/roasted-chicken-clementines-arak",
]


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "ottolenghi.co.uk" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # exatamente /pages/recipes/<slug> — exclui o índice /pages/recipes (2 segmentos),
    # categorias /pages/<algo>-recipes, produtos /products/, coleções /collections/ etc.
    if len(partes) != 3 or partes[0] != "pages" or partes[1] != "recipes":
        return False
    slug = partes[2].lower()
    if slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case


# Texto de âncoras de navegação que não é título de receita (a primeira página visitada
# pelo BFS só se referencia via o link "pular para o conteúdo").
_TITULO_LIXO = {"skip to content", "skip to content#maincontent", ""}


def coletar(limite: int) -> list[dict]:
    registros = base.coletar_por_crawl(SEEDS, CHEF, SITE, _e_receita, limite)
    # Saneia títulos vindos de âncoras de navegação: cai para o slug humanizado.
    for r in registros:
        if r["titulo"].strip().lower() in _TITULO_LIXO:
            r["titulo"] = base.humanizar_slug(r["url"])
    return registros
