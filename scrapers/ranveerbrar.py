"""Adaptador: Ranveer Brar — chef indiano, culinária da Índia, via sitemap.

Site WordPress (Yoast) servido por HTTP comum: o `/sitemap.xml` dá 404, mas o índice
fica em `/sitemap_index.xml` e há sub-sitemaps dedicados às receitas do chef
(`recipes-sitemap.xml` e `recipes-sitemap2.xml`, ~1500 URLs). As receitas ficam em
`/recipes/<slug>/`. Apesar de o front depender de JS, o sitemap responde via cliente
HTTP simples — não precisa de navegador.

Excluímos:
- `/user-recipes/<slug>/` (receitas enviadas por usuários, sub-sitemap separado);
- a própria listagem `/recipes/`;
- taxonomias/institucional (cuisines/ingredients/category/tag/web-stories etc.),
  garantidos pelo `sub_filtro` (só seguimos os recipes-sitemap) e pelo `_e_receita`.

Coleta APENAS a URL (localização) — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Ranveer Brar"
SITE = "ranveerbrar.com"
TECNICAS = ["sitemap"]
# O índice de sitemap usa o domínio sem www; mantemos consistente.
BASE_URL = "https://ranveerbrar.com"

# Yoast: índice em /sitemap_index.xml (o /sitemap.xml dá 404). descobrir_sitemaps()
# acha via robots.txt ou cai no /sitemap.xml — então apontamos direto pro índice.
SITEMAP_INDEX = "https://ranveerbrar.com/sitemap_index.xml"


# Só seguimos os sub-sitemaps de RECEITAS do chef (recipes-sitemap.xml / recipes-sitemap2.xml),
# evitando user_recipes (envio de usuários), páginas, produtos, taxonomias e web-stories.
def _sub_sitemap_de_receitas(url: str) -> bool:
    return bool(re.search(r"/recipes-sitemap\d*\.xml$", url.lower()))


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente dois segmentos: /recipes/<slug>  (exclui /recipes, /user-recipes/<x>)
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 2 or partes[0] != "recipes":
        return False
    slug = partes[1].lower()
    # slug kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    # Aponta direto para o índice Yoast (descobrir_sitemaps usaria /sitemap.xml → 404).
    return base.coletar_por_sitemap(SITEMAP_INDEX, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
