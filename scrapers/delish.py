"""Adaptador: Delish (EUA, Hearst) — via sitemap HTTP.

A marca é o "chef" (portal editorial da Hearst). Diferente das verificações automáticas
de status (que pegam 403/desafio), o sitemap abre normalmente via cliente Python: o
/sitemap.xml dá 404, mas o robots.txt aponta /sitemap_index.xml (200), que indexa
sub-sitemaps .gz. O sub-sitemap "content.*.xml.gz" mistura receitas, artigos, galerias,
vídeos e notícias — a separação fica TODA na URL (Princípio III: só localização).

Estrutura de URL da Hearst:
    /<seção>/.../a<ID>/<slug>/   -> ARTIGO único (receitas individuais usam isto)
    /<seção>/.../g<ID>/<slug>/   -> GALERIA / listicle / roundup (excluído)

Sinal confiável de RECEITA INDIVIDUAL: o caminho fica sob uma seção de receitas
(/recipe-ideas/ ou /recipes/) E tem um id de artigo a<ID>:
    /cooking/recipe-ideas/recipes/a54573/slow-cooker-crock-pot-hot-dogs-recipe/
    /cooking/recipe-ideas/a54969/sausage-balls-recipe/
    /cooking/recipes/a42453/boozy-pina-colada-dump-cake/

Exigir a<ID> já descarta as galerias g<ID>. Excluímos ainda subcaminhos /videos/ e
/news/ (existem dentro de /recipe-ideas/), e qualquer a<ID> fora das seções de receita
(how-to, food-news, /about/, perfis "what X eats in a day" etc.).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Delish"
SITE = "delish.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.delish.com/"

# Receita = caminho com um segmento de seção de receitas + id de artigo a<ID> + slug.
# (?<![a-z]) garante que o segmento seja exatamente "recipes"/"recipe-ideas" e não algo
# como "...recipes-roundup"; o a<ID> separa receita de galeria (g<ID>).
_SECAO_RECEITA_RE = re.compile(r"/(?:recipe-ideas|recipes)/")
_ARTIGO_RE = re.compile(r"/a\d+/[a-z0-9]+(?:-[a-z0-9]+)*/?$")
_SUBPATH_EXCLUIR = ("/videos/", "/news/")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    caminho = p.path
    # rejeita caminhos malformados (barra dupla)
    if "//" in caminho:
        return False
    if not _SECAO_RECEITA_RE.search(caminho):
        return False
    if any(sub in caminho for sub in _SUBPATH_EXCLUIR):
        return False
    # precisa terminar em /a<ID>/<slug>/ — receita individual (não galeria g<ID>)
    return bool(_ARTIGO_RE.search(caminho))


def coletar(limite: int) -> list[dict]:
    # sub_filtro: dentro do sitemap_index, só seguimos os sub-sitemaps de "content"
    # (onde ficam os artigos/receitas); ignora author, section, collection, tag etc.
    return base.coletar_por_sitemap(
        BASE_URL, CHEF, SITE, _e_receita, limite,
        sub_filtro=lambda u: "/content" in u or not u.endswith(".xml.gz"),
    )
