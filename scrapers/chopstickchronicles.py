"""Adaptador: Chopstick Chronicles (Shihoko Ura) — via sitemap.

WordPress/Yoast (atrás de Cloudflare, mas o sitemap responde ao cliente HTTP comum):
sitemap_index.xml → post-sitemap.xml. As receitas ficam em slug de raiz:
https://www.chopstickchronicles.com/<slug>/ (mesma forma do RecipeTin Eats).
Cozinha japonesa (país: Japão).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Shihoko Ura"
SITE = "chopstickchronicles.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.chopstickchronicles.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-sitemap / category-sitemap / favorite-sitemap (institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (institucionais, guias, índices).
_NAO_RECEITA = {
    "about", "about-me", "contact", "privacy-policy", "terms", "disclosure",
    "recipes", "category", "tag", "author", "subscribe", "shop", "cookbook",
    "my-account", "web-stories", "search", "newsletter", "faq", "press",
    "blog", "bento", "obento", "matcha", "daikon", "mirin", "natto", "gobo",
    "myoga", "kanten", "kinako", "calpis", "hojicha", "umeboshi", "yuzu-fruits",
    "understanding-japanese-food-terms", "how-to-use-chopsticks",
    "ultimate-sushi-guide", "essential-japanese-kitchenwares",
    "japanese-seasonings-condiments", "japanese-gift-wrapping",
    "japanese-thanksgiving-desserts", "miso-recipes", "matcha-recipes",
    "bento-menu-recipes", "bento-box-ideas", "japanese-food-substitutions",
    "onigiri-fillings", "ramen-noodle-recipes", "udon-noodle-recipes",
    "dango-recipes-you-can-make-at-home", "yoshoku-guide", "koji-seasonings",
    "japanese-hot-cake-mix", "how-to-wrap-bento-box", "how-to-cook-rice",
    "how-to-cook-rice-without-a-rice-cooker", "10-easy-japanese-recipes",
    "7-easy-and-delicious-japanese-tofu-recipes",
}

# Padrões em slugs que indicam roundup/guia/listicle (não uma receita única).
_PADROES_NAO_RECEITA = (
    "-guide", "guide-to", "how-to-use", "how-to-wrap", "things-to", "where-to",
    "easy-japanese-recipes", "japanese-tofu-recipes", "-recipes-you-can",
    "-ideas", "review", "giveaway", "best-of", "round-up", "roundup",
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
    # slug com palavras (kebab-case); evita ids/numéricos puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug)) and not slug.isdigit()


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
