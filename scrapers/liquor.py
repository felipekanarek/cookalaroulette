"""Adaptador: Liquor.com (marca, US — COQUETÉIS) via Internet Archive (Wayback).

Liquor.com é da Dotdash Meredith e fica atrás de Cloudflare: o /sitemap.xml raiz responde
200 (é só um índice), mas o sub-sitemap real (/sitemap_1.xml) devolve 403 com o desafio
"Just a moment..." da Cloudflare — bloqueio total ao cliente HTTP e ao navegador. Como o app
só precisa da URL para redirecionar (o humano abre normalmente), descobrimos as receitas pela
API CDX do Internet Archive, sem tocar no site (Princípio III/VII). 403 = vivo, não fatal.

As "receitas" aqui são coquetéis/drinks — entram no mesmo catálogo e contrato. O CHEF é a
marca (Liquor.com). O padrão de URL de uma receita de coquetel é slug de raiz terminado em
"-recipe-<id-numérico>":
    https://www.liquor.com/algonquin-cocktail-recipe-8383879
Artigos, listas ("15-cocktails-to-make-..."), reviews ("...-review-<id>"), guias, tendências
e páginas institucionais NÃO seguem esse sufixo e são excluídos pelo filtro abaixo.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Liquor.com"
SITE = "liquor.com"
TECNICAS = ["wayback"]
DOMINIO = "liquor.com"

# Sufixo que marca uma página de RECEITA de coquetel: "<slug>-recipe-<id>".
# (reviews terminam em "-review-<id>"; artigos/listas não têm o token "-recipe-<id>".)
_RECEITA = re.compile(r"-recipe-\d+$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (lixo do índice Wayback: barra dupla, etc.)
    if "//" in p.path:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita = exatamente um segmento de caminho: /slug-recipe-<id>
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    # slug em kebab-case limpo (evita fragmentos de JS/escapes que poluem o CDX)
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        return False
    return bool(_RECEITA.search(slug))


def coletar(limite: int) -> list[dict]:
    # As URLs de receita são esparsas no índice do Wayback (~0.1% das linhas, o resto é lixo
    # de JS/escapes e artigos). Sem filtro, 500 linhas rendem ~3 receitas. Com o filtro de
    # servidor NÃO-ancorado ".*-recipe-.*" (testado: devolve JSON válido e ~234 receitas em
    # 600 linhas) o rendimento dispara. ATENÇÃO: filtro ANCORADO com "[0-9]+" quebra o JSON
    # deste domínio — por isso o padrão fica solto aqui e a âncora "-recipe-<id>$" fica em
    # _e_receita (filtro fino local).
    return base.coletar_por_wayback(DOMINIO, CHEF, SITE, _e_receita, limite,
                                    cdx_filtro=".*-recipe-.*")
