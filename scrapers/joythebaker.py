"""Adaptador: Joy the Baker (Joy Wilson, EUA) — via sitemap.

WordPress/Yoast em Cloudflare, mas o cliente HTTP comum passa (não bloqueia): o
robots.txt aponta sitemap_index.xml → post-sitemap.xml + post-sitemap2.xml. As
receitas ficam sob /AAAA/MM/<slug>/ (3 segmentos de caminho).

Blog antigo (2008→hoje, ~1750 posts) com MUITO conteúdo pessoal/lifestyle além de
receitas: a coluna semanal "Let It Be Sunday" (>200 posts), o newsletter
"The Bakehouse Almanac", séries educativas "Baking 101", listas de leitura, guias
de presente, posts de viagem/maternidade, sorteios e podcast. Como o sitemap não
separa receita de post pessoal (mesma estrutura de URL), o filtro é por padrões de
slug: barramos os marcadores não-receita conhecidos e os roundups (link-hubs do tipo
"my-10-best-...-recipes"), preservando receitas individuais — inclusive as que
legitimamente citam lugares (ex.: "new-orleans-style-bbq-shrimp").

Coleta APENAS a URL — nunca o conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Joy Wilson"
SITE = "joythebaker.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://joythebaker.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / e-landing-page / web-story (institucional, landing, stories).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs exatos que não são receita.
_NAO_RECEITA = {
    "about", "about-joy", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "category", "tag", "author", "subscribe", "shop", "cookbook",
    "cookbooks", "my-account", "search", "newsletter", "faq", "press", "blog",
    "swabbing", "foodbuzzed", "thankful",
}

# Padrões em slugs que indicam post NÃO-receita: a coluna semanal, o newsletter,
# séries educativas, listas/guias, viagem, maternidade, sorteios, podcast, etc.
# (substring case-insensitive no slug). Mantém receitas que só citam um lugar.
_PADROES_NAO_RECEITA = (
    "let-it-be-sunday",         # coluna lifestyle semanal (>200 posts)
    "bakehouse-almanac",        # newsletter mensal
    "baking-101",               # série educativa (técnica, não receita única)
    "reading-list", "what-were-reading", "what-youre-reading", "in-the-stacks",
    "gift-guide", "gifts-im-giving", "giveaway", "-winner", "winners",
    "podcast", "-episode-", "camp-joy",
    "playlist", "true-crime", "book-club",
    "things-ive-learned", "things-i-do", "what-im-eating", "im-eating-right-now",
    "reading-recommendations", "cookbooks-im", "bucket-list",
    "behind-the", "from-the-archives", "cutting-room-floor",
    "dear-future", "dear-thirty", "dear-", "notes-from",
    "new-motherhood", "pregnant", "im-totally-freaking-out",
    "travel-essentials", "what-to-do-in", "things-to-do-in", "favorite-places",
    "favorite-things", "hello-new-orleans", "hello-again-new-orleans",
    "happy-tuesday-from", "happy-holidays", "lets-road-trip", "notes-from-the-road",
    "best-food-blogger", "blogging",
    "best-recipes", "best-cookie", "best-christmas", "best-birthday",
    "best-holiday", "best-cookies",  # roundups (link-hubs, não receita única)
    # tagarelice/anúncios da era 2008-2009 do blog (não-receita)
    "baggu", "love-you", "loves-you", "did-you-win", "-update", "update-",
    "secret-vintage", "handmade-aprons", "fancy-food", "picnic-rooftop",
    "rooftop-and-cupcakes", "picnic-opening", "who-wants-in", "inspiration-have",
    "heart-to-heart", "you-came-you-saw", "i-love-minted", "the-one-year-rewind",
    "we-do-dinner", "whole-lotta-etsy", "joy-the-baker-in-", "joy-the-baker-meets",
    "pink-hawaii", "mis-en-place", "food-and-wine", "have-any-to-spare",
    "tweet-tweet", "new-food-for-you", "bridge-watching", "verge-of-a-million",
    "en-route-to", "bakers-block", "twenty-eleven", "thirty-things-before",
    "scary-things", "before-thirty", "things-before", "penpals", "real-life-dinner",
)

# Roundups com nome no plural "...-recipes" (link-hubs, não receita única):
# ex. "every-which-way-pancake-recipes", "my-favorite-easter-brunch-recipes".
_RE_PLURAL_RECIPES = re.compile(r"-recipes$")

# Roundups do tipo "my-12-best-...", "my-favorite-...-recipes" (plural = lista).
_RE_ROUNDUP = re.compile(
    r"(?:^|-)(?:my-)?\d+-best-|favorite-[a-z-]+-recipes$|best-[a-z-]+-recipes$"
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    # estrutura de post WordPress: /AAAA/MM/<slug>/
    if len(partes) != 3:
        return False
    ano, mes, slug = partes[0], partes[1], partes[2].lower()
    if not (ano.isdigit() and len(ano) == 4 and mes.isdigit() and len(mes) == 2):
        return False
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if any(pad in slug for pad in _PADROES_NAO_RECEITA):
        return False
    if _RE_ROUNDUP.search(slug) or _RE_PLURAL_RECIPES.search(slug):
        return False
    # slug kebab-case com pelo menos duas palavras (receitas têm nome composto)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)+$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
