"""Adaptador: Marion's Kitchen (Marion Grasby) — via Internet Archive (Wayback).

O site (WordPress) fica TOTALMENTE atrás de Cloudflare: GET em /sitemap.xml e /robots.txt
devolve 403 com `cf-mitigated: challenge` (desafio anti-bot). Como o app só precisa da URL
para redirecionar (o humano abre normalmente), descobrimos as receitas pela API CDX do
Internet Archive, sem tocar no site (Princípio III/VII). 403 = vivo, não bloqueio fatal.

As receitas ficam em slug de raiz: https://www.marionskitchen.com/<slug>/ (mesma forma do
RecipeTin Eats). O site é grande e tem loja (food-products), artigos, coleções e páginas
institucionais — o filtro abaixo restringe às páginas de receita individual.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Marion Grasby"
SITE = "marionskitchen.com"
TECNICAS = ["wayback"]
DOMINIO = "marionskitchen.com"


# Slugs de raiz que NÃO são receitas: institucionais, loja/produtos, artigos, coleções,
# concursos, guias "how-to" e páginas de listagem. Receitas reais cujo nome contém
# "sauce"/"marinade"/"curry-paste" (ex.: chicken-with-black-bean-sauce) NÃO entram aqui —
# por isso a exclusão é por slug exato, não por substring desses termos.
_NAO_RECEITA = {
    # institucional / conta
    "about-us", "contact-us", "contact-us-2", "media-terms-and-conditions",
    "marions-kitchen-media", "behind-the-scene", "have-a-question-about-your-marions-kitchen-order",
    "ask-us-a-question-about-marions-kitchen-food-products",
    "download-partnership-terms-and-conditions",
    # listagens / hubs
    "all-recipes", "all-articles", "all-christmas-collections", "blogs",
    "article", "amp", "attachment", "ingredient", "cookbook",
    # loja / produtos
    "food-products", "food-range", "marinades", "marions-original-marinades",
    "marions-new-marinades-in-australia", "awesome-stuff-to-make-w-our-marinades-nz",
    "create-delicious-meals-with-your-favourite-marions-kitchen-product",
    "curry-paste", "massaman-curry-paste", "bao-bun-mix", "marion-s-kitchen-light-coconut-milk",
    "meal-kits-singapore-noodles",
    # coleções / agregadores editoriais (não são uma receita única)
    "collection", "collections", "collections-2", "collections-backup",
    "best-ever-chicken-recipes", "best-ever-dinner-inspo", "best-ever-mothers-day-recipes",
    "marions-best-ever-christmas-recipes", "marions-best-pasta-recipes", "marions-epic-bbq-recipes",
    "kid-friendly-recipes", "delicious-quick-and-easy-recipes", "easter-recipe-collection",
    "always-delicious", "all-about-curries", "all-about-eggs", "all-about-pork-belly",
    "classic-asian-mains", "christmas-sauces-sides", "christmas-salads", "holiday-season",
    "10-minute-meals", "15-minute-meals", "30-minute-meals",
    # concursos / promoções / duplicatas / rascunhos
    "cookbook-competition", "cookbook-winners-2022", "curry-cooking-competition",
    "curry-cooking-competition-terms-and-conditions", "christmas-competition",
    "mako-winners-2022", "makowokmasterclass", "duplicated-recipes-2021",
    "chilli-sauce-old", "classi", "express-thai-c",
}

# Padrões em slugs que marcam não-receita de forma confiável (sufixos/prefixos de hub).
_PADROES_NAO_RECEITA = (
    "-collection", "-collections", "competition", "terms-and-conditions",
    "-winners", "how-to-",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # rejeita caminhos malformados (barra dupla "//slug" presente no índice do Wayback) —
    # evita emitir URL torta e duplicar uma receita que coletamos na forma limpa.
    if "//" in p.path:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receita = exatamente um segmento de caminho: /slug/  ou  /slug
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros e arquivos
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    # Sem cdx_filtro: o regex anchored do servidor CDX (filter=original:) quebra a resposta
    # JSON para este domínio; o filtro fino fica todo em _e_receita. O `limit` interno do
    # helper (max(500, limite*20)) já traz slugs de raiz suficientes (≈55 em 500 linhas).
    return base.coletar_por_wayback(DOMINIO, CHEF, SITE, _e_receita, limite)
