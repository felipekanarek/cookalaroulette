"""Adaptador: The Woks of Life (família Leung — China/EUA) — via sitemap.

WordPress/Yoast: sitemap raiz limpo (index → post-sitemap.xml + post-sitemap2.xml),
receitas em slug de raiz https://thewoksoflife.com/<slug>/ (mesmo padrão da RecipeTin
Eats). HTTP comum funciona (sem 403). Atenção: o dominio COM www dá 404 — use SEM www.

O post-sitemap mistura receitas com guias ("how-to-...", "what-is-..."), roundups
("...-recipes", "N-...-meals") e posts institucionais. Filtramos por URL (predicado +
denylist), do mesmo jeito que a RecipeTin Eats — coletando só a LOCALIZAÇÃO, sem abrir
cada página (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "The Woks of Life"
SITE = "thewoksoflife.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://thewoksoflife.com"  # COM www → 404; usar SEM www


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), pulando
# page/category/author-sitemap (páginas institucionais, taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas individuais.
_NAO_RECEITA = {
    "blog", "introductions", "recipes", "about", "about-us", "contact",
    "privacy-policy", "terms", "subscribe", "newsletter", "shop", "search",
    "faq", "press", "cooking-methods-used-in-chinese-cuisine",
    "top-quick-and-easy-noodle-soups",
}

# Prefixos de guias/artigos (não receitas).
_PREFIXOS_NAO_RECEITA = ("how-to-", "what-is-", "things-to-do-")

# Trechos que marcam roundups/guias/institucionais.
_TRECHOS_NAO_RECEITA = (
    "-recipes", "cookbook", "-guide", "-giveaway", "-update",
    "food-guide", "taste-test", "-how-to",
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
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    if slug.startswith(_PREFIXOS_NAO_RECEITA):
        return False
    if any(t in slug for t in _TRECHOS_NAO_RECEITA):
        return False
    # roundups com prefixo numérico: "25-last-minute-meals", "10-...-hacks"
    if re.match(r"^[0-9]+-.*-(meals|hacks|ideas|dishes)", slug):
        return False
    # slug em kebab-case (exclui underscore, ids puros)
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
