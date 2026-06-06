"""Adaptador: Simply Delicious (Alida Ryder, África do Sul) — via sitemap.

Blog WordPress grande com Yoast: sitemap_index.xml -> post-sitemap.xml /
post-sitemap2.xml (onde ficam as receitas). Receitas em slug de raiz:
https://simply-delicious-food.com/<slug>/ (padrão RecipeTin Eats).

O post-sitemap mistura receitas individuais com MUITOS posts editoriais: roundups
("...-recipes", "...-ideas"), listicles ("the-best-...", "top-...", "what-to-..."),
planos de refeição ("meal-plan-..."), guias/dicas e páginas institucionais. Filtramos
tudo isso via predicado de slug, mantendo só receitas individuais reais.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Alida Ryder"
SITE = "simply-delicious-food.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://simply-delicious-food.com"


# Só seguimos os sub-sitemaps de POSTS (post-sitemap.xml / post-sitemap2.xml),
# evitando page-sitemap / category-sitemap (institucionais e taxonomia).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (páginas institucionais e meta-posts conhecidos).
_NAO_RECEITA = {
    "blog", "about", "about-me", "contact", "privacy-policy", "terms",
    "recipes", "recipe-index", "category", "tag", "subscribe", "shop",
    "cookbooks", "cookbook", "work-with-me", "press", "faq", "search",
    "newsletter", "portfolio", "ingredient-substitutions",
    "food-photography-guide", "food-styling-tips",
    "mom", "conversion-chart", "pinned-recipe", "circus-party",
    "oyster-box", "startover-with-22seven",
}

# Fragmentos que denunciam roundup / listicle / conteúdo editorial (não-receita).
_PADROES_NAO_RECEITA = (
    r"recipes$",          # ...-recipes  (roundups)
    r"ideas$",            # ...-ideas
    r"appetizers$",       # christmas-appetizers (roundup)
    r"-sides$",           # thanksgiving-sides (roundup)
    r"-meals$",           # easy-freezer-meals (roundup)
    r"^stocking-",        # stocking-a-pantry (guia)
    r"^the-\d+-best-",    # the-20-best-...
    r"^the-best-",        # the-best-...
    r"^our-\d*-?best-",   # our-best-... / our-10-best-...
    r"^top-",             # top-...
    r"^\d+-easy-",        # 4-easy-... / 5-easy-...
    r"^what-to-",         # what-to-serve-with-...
    r"^how-to-",          # how-to-... (técnicas/guia, não receita individual)
    r"^meal-plan",        # meal-plan-28-of-2025
    r"-guide$",           # ...-guide
    r"-menu",             # ...-menu / menu-...
    r"-week$",            # ...-week
    r"giveaway",
    r"^win-",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    # exatamente um segmento de caminho: /slug/  ou  /slug  (slug de raiz)
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    # slug em kebab-case (palavras com hífen); exclui ids/underscores
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        return False
    # rejeita roundups / listicles / posts editoriais
    if any(re.search(pat, slug) for pat in _PADROES_NAO_RECEITA):
        return False
    return True


def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                    sub_filtro=_sub_sitemap_de_posts)
