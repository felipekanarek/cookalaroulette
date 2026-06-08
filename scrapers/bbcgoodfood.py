"""Adaptador: BBC Good Food (UK, editorial) — via sitemap.

A marca é o "chef" (publicação editorial britânica, acervo enorme). O site é descrito
como "bloqueado na verificação", mas o cliente HTTP do projeto (base.HEADERS, UA honesto)
passa: GET em /sitemap.xml devolve 200 (servido via Amazon S3/Fastly). Por isso usamos a
técnica preferida — sitemap — sem precisar de navegador nem Wayback.

Estrutura do sitemap: um índice raiz aponta para sub-sitemaps trimestrais por tipo de
conteúdo (`<ano>-<trimestre>-<tipo>.xml`): post, page, editorialList, review, glossary e
**recipe**. Só seguimos os `*-recipe.xml` (sub_filtro), que concentram as receitas.

Dentro do recipe-sitemap convivem dois prefixos:
  - https://www.bbcgoodfood.com/recipes/<slug>        ← receita individual (o que queremos)
  - https://www.bbcgoodfood.com/premium/<slug>        ← receita paga (excluída: o redirect
    levaria o usuário a um paywall, não a uma receita aberta)

Excluímos ainda, sob /recipes/:
  - guias "how-to-..." (ex.: /recipes/how-to-make-polenta, /recipes/how-to-cook-salmon);
  - URLs legadas com categoria no caminho (/recipes/<categoria>/<slug>/) — raríssimas e
    são hubs/forma antiga; ficamos só com o formato canônico /recipes/<slug>;
  - hubs de taxonomia /recipes/collection/..., /recipes/category/..., reviews, health etc.
    (já naturalmente fora por terem mais de um segmento de caminho).

Coleta APENAS a URL — nunca o conteúdo (Princípio III). Título derivado do slug.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "BBC Good Food"
SITE = "bbcgoodfood.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.bbcgoodfood.com"


# Só seguimos os sub-sitemaps de RECEITA (ex.: 2026-Q2-recipe.xml), ignorando
# post/page/editorialList/review/glossary (artigos, taxonomia, institucional).
def _sub_sitemap_de_receitas(url: str) -> bool:
    return url.lower().rstrip("/").endswith("-recipe.xml")


# Primeiro segmento após /recipes/ que denota hub/taxonomia, não receita individual.
_NAO_RECEITA = {
    "collection", "collections", "category", "categories", "cuisine",
    "cuisines", "courses", "course", "health", "howto", "how-to",
}


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # caminhos malformados (barra dupla)
    if "//" in p.path:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita canônica = exatamente /recipes/<slug>  (dois segmentos)
    # → exclui /premium/<slug>, /recipes/category/<slug>/, /recipes/collection/... etc.
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False
    slug = partes[1].lower()
    if slug in _NAO_RECEITA:
        return False
    # guias "how-to-..." não são receitas
    if slug.startswith("how-to-"):
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros e arquivos
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_receitas)
