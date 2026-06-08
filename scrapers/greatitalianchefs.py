"""Adaptador: Great Italian Chefs — via sitemap.

Site editorial/marca (irmão do Great British Chefs, mesma infraestrutura): o CHEF é a
própria marca "Great Italian Chefs". O sitemap único (urlset, não índice) fica acessível
por cliente HTTP comum (HTTP 200, text/xml). As receitas individuais ficam sob
https://www.greatitalianchefs.com/recipes/<slug> — sempre EXATAMENTE um segmento após
/recipes/ (verificado: 637 URLs nessa forma). Existe também a página de listagem
/recipes (sem slug), que o filtro exclui. Outras seções (how-to-cook, features,
collections, restaurants, chefs, ...) não são receitas e são descartadas.

ATENÇÃO: o robots.txt deste domínio anuncia, por engano, o sitemap do SITE-IRMÃO
(`Sitemap: https://www.greatbritishchefs.com/sitemap.xml`). Por isso NÃO usamos
`base.coletar_por_sitemap` (que descobre o sitemap via robots.txt e traria receitas
britânicas, rejeitadas pelo filtro de netloc → 0 resultados). Apontamos direto para
o /sitemap.xml deste domínio via `base.iter_urls_sitemap`.

Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Great Italian Chefs"
SITE = "greatitalianchefs.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.greatitalianchefs.com"
SITEMAP_URL = "https://www.greatitalianchefs.com/sitemap.xml"


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita = exatamente /recipes/<slug>  (a listagem /recipes tem 1 segmento → excluída)
    if len(partes) != 2 or partes[0].lower() != "recipes":
        return False
    slug = partes[1].lower()
    # slug em kebab-case com palavras; evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    # Lê o sitemap DESTE domínio diretamente (não via robots.txt — ver docstring).
    vistos = set()
    registros: list[dict] = []
    for url in base.iter_urls_sitemap(SITEMAP_URL):
        if len(registros) >= limite:
            break
        if url in vistos or not _e_receita(url):
            continue
        vistos.add(url)
        r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(url), url)
        if base.registro_valido(r):
            registros.append(r)
    return registros
