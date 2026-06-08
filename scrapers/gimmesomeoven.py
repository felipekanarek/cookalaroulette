"""Adaptador: Gimme Some Oven (Ali Martin) — via Internet Archive (Wayback).

O site está totalmente atrás de Cloudflare (cf-mitigated: challenge em TODA requisição,
inclusive /sitemap.xml e /robots.txt). Não dá para coletar por sitemap nem por crawl: o
cliente HTTP recebe o desafio anti-bot. Usamos a API CDX do Internet Archive para descobrir
as URLs (fonte pública de descoberta) — o app só precisa da URL para redirecionar, e a
verificação trata 403 como "página existe" (confirmado: receitas reais devolvem 403 vivo).

Estrutura: WordPress com slugs de RAIZ (sem prefixo /recipes/):
    https://www.gimmesomeoven.com/<slug>/
A taxonomia fica em /category/, /tag/, /author/, /about. O site mistura muito post de
"lifestyle" (giveaways, gift-guides, roundups, viagens, "things I learned"), então o filtro
exclui esses padrões com cuidado. Distinção-chave: receita real termina em "-recipe"
(singular) ou é prato simples; roundup/categoria termina em "-recipes" (plural).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Ali Martin"
SITE = "gimmesomeoven.com"
TECNICAS = ["wayback"]
DOMINIO = "gimmesomeoven.com"


# Slugs de raiz que NÃO são receitas (institucionais / taxonomia / seções).
_NAO_RECEITA = {
    "about", "contact", "privacy-policy", "terms", "disclosure", "disclaimer",
    "category", "tag", "author", "recipes", "all-recipes", "recipe-index",
    "subscribe", "shop", "cookbook", "cookbooks", "my-account", "web-stories",
    "search", "newsletter", "faq", "press", "blog", "advertise", "work-with-me",
    "media", "page", "feed", "embed", "wp-json", "wp-admin", "wp-login.php",
    "comment-page", "go", "refer", "recommend", "recommends", "well-known",
    "home", "start-here", "favorites", "resources",
}

# Substrings em slugs que denunciam post NÃO-receita (lifestyle, sorteio, promo, lista).
_PADROES_NAO_RECEITA = (
    "giveaway", "gift-guide", "gift-guides", "gift-idea", "gift-card",
    "giftcard", "i-learned", "things-i", "road-trip", "and-single",
    "reader-survey", "annual-reader", "black-friday", "cyber-monday",
    "behind-the", "currently", "this-week", "aldi-101", "how-to-shop",
    "why-i-shop", "what-to-buy", "25-days-of-giveaways", "favorite-things",
    "my-favorite-things", "life-lately", "weekend-", "our-wedding",
    "our-trip", "my-trip", "travel-", "-travel", "holiday-gift",
    "amazon-giveaway", "instagram-giveaway", "winner", "sponsored",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento de caminho: /slug/  ou  /slug
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA:
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    # slug em kebab-case com palavras; evita ids/numéricos puros
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug) or slug.isdigit():
        return False
    # Roundups e páginas de categoria terminam em "-recipes" (plural): listas do tipo
    # "15-fall-pizza-recipes", "bread-recipes", "chicken-breast-recipes". Receita
    # individual termina em "-recipe" (singular) ou em nome de prato.
    if slug.endswith("-recipes"):
        return False
    # Listas numeradas ("15-cobblers-crumbles-crisps", "10-favorite-...", "15-thanksgiving-
    # side-dishes"): começam com número. PORÉM "N-minute/hour/ingredient/..." são receitas
    # reais (quantificadores de tempo/ingrediente), não listas. Bloqueia o número-líder a
    # menos que seguido de uma unidade de receita conhecida.
    m = re.match(r"^(\d{1,4})-([a-z]+)", slug)
    if m:
        unidade = m.group(2)
        _UNIDADES_RECEITA = {
            "minute", "minutes", "min", "hour", "hours", "hr",
            "ingredient", "ingredients", "layer", "layers", "clove", "cloves",
            "day", "days", "week", "bean",
        }
        if unidade not in _UNIDADES_RECEITA:
            return False
    return True


def coletar(limite: int) -> list[dict]:
    # Sem cdx_filtro: o índice CDX deste domínio tem MUITO ruído (comment-page, feed,
    # embed, query-strings, lixo de JS antigo) e vem ordenado por urlkey — os primeiros
    # 500 registros (janela mínima do helper) ficam presos nos slugs "0-9..." e rendem
    # poucas receitas. Inflamos o piso do `limite` repassado ao helper (que dimensiona a
    # janela CDX em ~limite*20) para varrer fundo o suficiente, e fatiamos no fim. O
    # filtro local `_e_receita` faz a limpeza fina dos slugs de raiz.
    alvo = max(limite, 60)  # ~1200 linhas CDX → janela com receitas de todo o alfabeto
    registros = base.coletar_por_wayback(DOMINIO, CHEF, SITE, _e_receita, alvo)
    return registros[:limite]
