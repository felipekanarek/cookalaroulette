"""Adaptador: Food & Wine (EUA, Dotdash Meredith) — via Internet Archive (Wayback).

A marca é o "chef" (revista editorial). O /sitemap.xml RAIZ abre (200) e é só um
sitemapindex; os sub-sitemaps (sitemap_1.xml, sitemap_2.xml) ficam atrás de um desafio
Cloudflare ("Just a moment...", 403) mesmo com User-Agent de navegador. As próprias
páginas de receita também devolvem 403 ao bot, mas abrem normalmente para humanos — e o
app só precisa da URL para redirecionar. Por isso descobrimos as receitas pela API CDX do
Internet Archive, sem tocar no site (Princípio III/VII). 403 = vivo, não bloqueio fatal.

Estrutura de URL (Dotdash moderno): receita = slug de RAIZ terminando em
`-recipe-<id>` (id numérico), num único segmento de caminho:

    /alaskan-halibut-olympia-recipe-11871772   -> RECEITA
    /adonis-cocktail-recipe-11718301           -> RECEITA (coquetel)
    /50-50-martini-recipe-8741173              -> RECEITA

Excluímos o ruído que o CDX captura:
  - query/login: /account/signin?returnURL=...   (some por ter query / não bater o regex)
  - artigos legados multi-segmento: /cooking-techniques/grilled-nopales-recipe-angie-vargas
    (mais de um segmento e/ou sem id numérico final → não bate o regex canônico);
  - artigos editoriais cujo slug contém "recipe" por acaso e ainda termina em -recipe-<id>
    (ex.: angostura-bitters-secret-recipe-... = matéria "How Angostura...Secret Recipe";
    recipe-developer..., recipe-collection...) → barrados pela lista de guarda.

O sinal confiável de RECEITA INDIVIDUAL é o caminho canônico `^/<slug>-recipe-<id>$`
(segmento único, termina em id numérico).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Food & Wine"
SITE = "foodandwine.com"
TECNICAS = ["wayback"]
DOMINIO = "foodandwine.com"

# Receita canônica: /<slug-kebab>-recipe-<id-numérico>  (segmento único de caminho).
# O id final separa a receita real dos artigos legados (/secao/...-recipe-autor, sem id).
_RECEITA_RE = re.compile(r"^/[a-z0-9]+(?:-[a-z0-9]+)*-recipe-\d+$")

# Frases editoriais que terminam coincidentemente em -recipe-<id> mas são MATÉRIA, não receita.
_GUARDA_NAO_RECEITA = (
    "secret-recipe",        # "...maintained its secret recipe..."
    "family-recipe",
    "original-recipe",
    "recipe-developer",     # perfis/contratações
    "recipe-collection",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla do índice Wayback)
    if "//" in p.path:
        return False
    if not _RECEITA_RE.match(p.path):
        return False
    slug = p.path.lstrip("/").lower()
    return not any(g in slug for g in _GUARDA_NAO_RECEITA)


def coletar(limite: int) -> list[dict]:
    # Sub-sitemaps bloqueados por Cloudflare (403) → descoberta via Wayback CDX, como
    # saveur.py. Filtro no servidor por slugs contendo "-recipe-" reduz a resposta (domínio
    # grande); o filtro fino (forma canônica + guarda editorial) fica em _e_receita.
    # base.coletar_por_wayback já: normaliza http→https, tira query/fragmento, dedup,
    # deriva título do slug (humanizar_slug) e valida o contrato.
    return base.coletar_por_wayback(DOMINIO, CHEF, SITE, _e_receita, limite,
                                    cdx_filtro=".*-recipe-.*")
