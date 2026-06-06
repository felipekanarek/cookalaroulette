"""Adaptador: Helen Le (Vietnã) — via sitemap.

Ressalva importante: o domínio original danangcuisine.com FOI DESATIVADO — hoje é uma
página estacionada da GoDaddy ("domain for sale"), sem nenhuma receita. O conteúdo da
chef migrou para o site WordPress atual `helenrecipes.com` (Helen's Recipes Official
Website), que é onde estão as receitas vivas e redirecionáveis. Coletamos de lá.

O site é WordPress com sitemap Yoast (`/sitemap_index.xml`; o robots.txt aponta para
sitemaps decoy que dão 404). As receitas em inglês ficam em slug de raiz:
https://helenrecipes.com/<slug>/  — com duplicatas localizadas em /vi/ (vietnamita) e
/ja/ (japonês), além de páginas de taxonomia em /recipes/<categoria> e páginas
institucionais. Filtramos para ficar só nas receitas em inglês (slug de raiz).

Só localização (chef/site/titulo/url), nunca conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Helen Le"
SITE = "helenrecipes.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://helenrecipes.com"
# O robots.txt aponta para sitemaps decoy (sitemap215.xml ... → 404), o que faz a
# descoberta padrão via robots quebrar. Apontamos direto para o índice Yoast real.
SITEMAP_INDEX = "https://helenrecipes.com/sitemap_index.xml"

# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page/category/tag/ingredient/cuisine/author-sitemaps (institucionais e taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz (1 segmento) que NÃO são receitas: páginas institucionais, cobertura de
# mídia, guias de viagem/turismo e listas de restaurantes ("top N ... in da nang").
_NAO_RECEITA = {
    "watch", "recipes", "portfolio", "contacts", "in-the-media", "pho-my-cooking-studio",
    "about-me", "recommended-places-in-da-nang", "travel", "cookbook", "work-with-us",
    "masterclass", "home-en", "world-travel", "viet-nam", "test",
}

# Sinais textuais de post que NÃO é receita (cobertura de mídia / turismo / artigos).
_PADROES_NAO_RECEITA = (
    "top-4-", "top-5-", "top-10-", "top-nhung-", "must-try-", "must-visit",
    "in-da-nang", "in-danang", "to-the-world", "to-the-outside-world",
    "global-exposure", "helens-recipes-meet-the-youtuber", "articles-about-helen",
    "introduces-new-culinary-ambassador", "rising-chef-challenge",
    "things-i-swear-by", "coffee-culture", "coffee-beans-that-shape",
    "exploring-", "discover-the-", "what-are-the-attractive",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # exatamente um segmento: /slug/  (exclui /vi/..., /ja/..., /recipes/<cat>, etc.)
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(sinal in slug for sinal in _PADROES_NAO_RECEITA):
        return False
    # kebab-case ascii (exclui slugs percent-encoded de outras línguas)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    # Iteramos direto o índice Yoast (o robots.txt só tem sitemaps decoy 404), reusando o
    # helper iter_urls_sitemap (recursa nos post-sitemaps via sub_filtro). Montagem de
    # registro/validação idêntica a base.coletar_por_sitemap.
    vistos = set()
    registros: list[dict] = []
    for url in base.iter_urls_sitemap(SITEMAP_INDEX, sub_filtro=_sub_sitemap_de_posts):
        if len(registros) >= limite:
            break
        if url in vistos or not _e_receita(url):
            continue
        vistos.add(url)
        r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(url), url)
        if base.registro_valido(r):
            registros.append(r)
    return registros
