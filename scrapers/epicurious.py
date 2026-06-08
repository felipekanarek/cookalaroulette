"""Adaptador: Epicurious (EUA, Condé Nast) — via sitemap HTTP.

A marca é o "chef" (portal editorial Condé Nast, acervo enorme). O site é bloqueado na
etapa de verificação por humanos, mas o sitemap responde 200 ao cliente HTTP honesto
(CloudFront, sem desafio anti-bot) — então coletamos as URLs direto do sitemap, sem
navegador (Princípio III/VII: só a localização, nunca o conteúdo).

Estrutura do sitemap (https://www.epicurious.com/sitemap.xml):
  - índice mensal: <loc>.../sitemap-YYYY-MM.xml</loc> (um urlset por mês);
  - cada urlset mistura artigos editoriais e receitas. A separação é limpa e fica TODA na
    URL:
        /recipes/food/views/<slug>   -> RECEITA individual  (ex.: .../ba-syn-peaches-foster)
        /recipes-menus/...           -> artigo/lista        (excluído)
        outros caminhos              -> editorial/galeria    (excluído)

Basta exigir o caminho canônico `^/recipes/food/views/<slug>$` (slug único de kebab-case,
sem subníveis — confirmado: nenhuma receita tem segmento extra após o slug). Isso descarta
galerias, artigos /recipes-menus/, páginas de tag/contributor e o resto do ruído.

`sub_filtro` limita a recursão do índice aos sitemaps mensais (sitemap-YYYY-MM.xml), que é o
único tipo listado no índice raiz.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Epicurious"
SITE = "epicurious.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.epicurious.com"

# Receita canônica: /recipes/food/views/<slug-kebab>  (sem subníveis após o slug).
_RECEITA_RE = re.compile(r"^/recipes/food/views/[a-z0-9]+(?:-[a-z0-9]+)*$")

# Prefixo de CMS na minoria das URLs (sindicação Bon Appétit): "ba-syn-" vira "Ba Syn ..."
# em humanizar_slug, sujando o título sem ser parte do nome do prato. Removemos só do RÓTULO
# (a URL fica intacta). Espelha o tratamento do prefixo "recipe-" no adaptador The Kitchn.
_PREFIXO_TITULO_RE = re.compile(r"^Ba Syn\s+", re.IGNORECASE)

# Sub-sitemaps mensais do índice raiz: /sitemap-YYYY-MM.xml
_MENSAL_RE = re.compile(r"/sitemap-\d{4}-\d{2}\.xml$")


def _sub_filtro(url: str) -> bool:
    return bool(_MENSAL_RE.search(url))


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla)
    if "//" in p.path:
        return False
    return bool(_RECEITA_RE.match(p.path))


def coletar(limite: int) -> list[dict]:
    registros = base.coletar_por_sitemap(
        BASE_URL, CHEF, SITE, _e_receita, limite, sub_filtro=_sub_filtro
    )
    # Limpa o prefixo de CMS do título (não da URL); se sobrar vazio, mantém o original.
    for r in registros:
        limpo = _PREFIXO_TITULO_RE.sub("", r["titulo"]).strip()
        if limpo:
            r["titulo"] = limpo
    return registros
