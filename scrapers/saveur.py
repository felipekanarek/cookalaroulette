"""Adaptador: Saveur (EUA, editorial) — via Internet Archive (Wayback).

A marca é o "chef" (revista editorial). O site fica TOTALMENTE atrás de Cloudflare:
GET em /, /sitemap.xml e /sitemap_index.xml devolve 403 (desafio anti-bot) mesmo com
User-Agent honesto. Como o app só precisa da URL para redirecionar (o humano abre
normalmente), descobrimos as receitas pela API CDX do Internet Archive, sem tocar no site
(Princípio III/VII). 403 = vivo, não bloqueio fatal.

Estrutura de URL: tudo fica em slug de raiz — https://www.saveur.com/<slug>/ — tanto
receitas individuais quanto artigos editoriais e listas ("roundups"). O sinal confiável
de RECEITA INDIVIDUAL é o sufixo singular `-recipe` no slug
(ex.: barbacoa-recipe, avocado-soup-recipe, baked-alaska-recipe).
Excluímos:
  - listas/roundups: sufixo plural `-recipes` e prefixos de contagem ("12-...", "25-...");
  - artigos editoriais, guias, notícias, gift-guides, blog-awards etc. (não terminam em -recipe);
  - páginas institucionais / taxonomia / autor.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Saveur"
SITE = "saveur.com"
TECNICAS = ["wayback"]
DOMINIO = "saveur.com"


# Slugs de raiz que NÃO são receitas mesmo terminando coincidentemente perto de "-recipe".
# (defesa extra; o filtro principal é o sufixo -recipe + ausência de prefixo de contagem)
_NAO_RECEITA = {
    "about-us", "about", "contact", "contact-us", "privacy-policy", "terms",
    "terms-of-service", "newsletter", "subscribe", "advertise", "masthead",
    "sitemap", "search", "author", "tag", "category", "recipes",
}

# Padrões em slugs que marcam não-receita / listas de forma confiável.
_PADROES_NAO_RECEITA = (
    "-recipes",            # plural → lista/roundup ("best-mango-recipes")
    "best-",               # roundups editoriais
    "-gift-guide", "gift-guide-",
    "blog-awards", "best-food-blog",
    "how-to-",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla "//slug" no índice do Wayback)
    if "//" in p.path:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita = exatamente um segmento de caminho: /slug/  ou  /slug
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    # sinal positivo: termina em "-recipe" (singular) — receita individual
    if not slug.endswith("-recipe"):
        return False
    # listas começam com contagem ("12-risotto-...", "25-thanksgiving-...")
    if re.match(r"^\d+-", slug):
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros e arquivos (.jsp etc.)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    # Filtro no servidor CDX por slugs que contêm "-recipe" reduz drasticamente a resposta
    # (o domínio é grande); o filtro fino (singular vs. plural, contagem) fica em _e_receita.
    return base.coletar_por_wayback(DOMINIO, CHEF, SITE, _e_receita, limite,
                                    cdx_filtro=".*-recipe.*")
