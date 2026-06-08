"""Adaptador: Bon Appétit (EUA, Condé Nast) — via sitemap.

A marca é o "chef" (revista editorial da Condé Nast). Apesar da reputação da Condé Nast
de bloquear bots, o `/sitemap.xml` de bonappetit.com responde 200 ao cliente HTTP comum
(há rate-limit por header `x-ratelimit-*`, mas o `base.get` já é educado com PAUSA). O
robots.txt aponta o sitemap, e o índice é mensal:

    /sitemap.xml                 -> sitemapindex de /sitemap-AAAA-MM.xml (mês a mês)
    /sitemap-2026-06.xml         -> urlset do mês

`base.coletar_por_sitemap` recursa nesse índice aninhado automaticamente. Caso o site
passe a bloquear o cliente HTTP (403/429), `base.get` levanta BloqueioError e o
orquestrador trata como "bloqueado-pulado" (403 = vivo) — não contornamos proteção.

Estrutura de URL — receita individual fica SEMPRE sob /recipe/<slug> (singular):

    /recipe/<slug>          -> RECEITA   (ex.: /recipe/peaches-foster)
    /story/<slug>           -> artigo editorial   (excluído)
    /gallery/<slug>         -> galeria de fotos    (excluído)
    /recipes/...            -> hubs/listas (plural)  (excluído)
    /contributor/, /tag/... -> taxonomia/autor       (excluído)

Coleta APENAS a localização (URL); nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Bon Appétit"
SITE = "bonappetit.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.bonappetit.com"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla)
    if "//" in p.path:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita = exatamente dois segmentos: /recipe/<slug>
    if len(partes) != 2 or partes[0] != "recipe":
        return False
    slug = partes[1].lower()
    # slug em kebab-case com ao menos uma letra; evita ids/numéricos puros
    return bool(re.match(r"^(?=[a-z0-9-]*[a-z])[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
