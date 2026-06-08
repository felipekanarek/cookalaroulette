"""Adaptador: Leite's Culinaria (David Leite) — via Internet Archive (Wayback).

O site está totalmente atrás de Cloudflare (cf-mitigated: challenge em /sitemap.xml e
/robots.txt), então a coleta usa o CDX do Internet Archive — descobrimos só a URL, nunca
o conteúdo (Princípio III). O app só precisa da URL viva para redirecionar; o verificador
trata 403 como "existe".

WordPress/Yoast antigo, com MUITO conteúdo não-receita (artigos, colunas, listas). A boa
notícia é que a URL carrega o TIPO do post no slug, num padrão limpíssimo:

    /<id>/recipes-<slug>.html   -> RECEITA   (861 de 922 posts no post-sitemap)
    /<id>/writings-<slug>.html  -> artigo/coluna   (excluído)
    /<id>/roundups-<slug>.html  -> lista/coletânea  (excluído)
    /<id>/faves-<slug>.html     -> favoritos         (excluído)

Basta exigir o segmento de tipo `recipes-` para separar receita de artigo. O CDX devolve
ruído (.../feed, .../print/, ?replytocom=, ?ignorenitro=); o filtro abaixo só aceita a URL
canônica terminada em `recipes-<slug>.html`, e o base.py já remove query/fragmento.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "David Leite"
SITE = "leitesculinaria.com"
TECNICAS = ["wayback"]

# URL canônica de receita: /<id-numérico>/recipes-<slug>.html
_RECEITA_RE = re.compile(r"^/\d+/recipes-[a-z0-9-]+\.html$")


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # base.coletar_por_wayback já tira ?query e #frag; aqui exigimos o caminho canônico,
    # o que descarta variantes /feed, /print/, /amp etc. e todo prefixo != "recipes-"
    # (writings-, roundups-, faves-, categorias, autor, institucional).
    return bool(_RECEITA_RE.match(p.path))


def coletar(limite: int) -> list[dict]:
    # cdx_filtro reduz a resposta do CDX no servidor (só URLs com /recipes-...html);
    # _e_receita faz o filtro final (canoniza e exclui feed/print/comentários).
    return base.coletar_por_wayback(
        SITE, CHEF, SITE, _e_receita, limite,
        cdx_filtro=r".*/recipes-.*\.html",
    )
