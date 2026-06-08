"""Adaptador: Rick Stein (Reino Unido) — via listagem paginada.

O site é parte loja/restaurante/escola de cozinha; as RECEITAS vivem na categoria de blog
`/blog-categories/rick_stein_recipes/` (paginada, ~9 por página, ~14 páginas). O sitemap
mistura receitas com notícias/eventos/restaurantes e não tem um sitemap só de receitas, então
a fonte mais limpa é a própria listagem da categoria de receitas: cada página só linka receitas.

As receitas aparecem como posts em `/blog/<slug>/` (a maioria, mas nem todas, termina em
`-recipe`) e, em acervo antigo, como raiz `/recipe-<slug>-from-rick-steins-<livro>/`.
Excluímos loja, restaurantes, escola, eventos, sobre, categorias, feed e paginação.

APENAS a URL é coletada (Princípio III) — nunca o conteúdo. Cloudflare deixa o cliente HTTP
comum passar (200 no sitemap e nas listagens), então não precisa de navegador.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Rick Stein"
SITE = "rickstein.com"
TECNICAS = ["listagem"]

# A categoria de receitas é paginada; 14 páginas cobrem o acervo (page/14 ainda responde 200).
# Geramos com folga (até 20) — páginas inexistentes dão 404 e são isoladas pelo helper.
_LISTAGEM_BASE = "https://rickstein.com/blog-categories/rick_stein_recipes/"
URLS_LISTAGEM = [_LISTAGEM_BASE] + [
    "{}page/{}/".format(_LISTAGEM_BASE, n) for n in range(2, 21)
]

# Slugs de /blog/ que são posts, não receitas (notícias, atualizações, episódios, viagens).
# A listagem da categoria de receitas raramente os expõe, mas filtramos por garantia.
_PALAVRAS_NAO_RECEITA = (
    "episode", "long-weekends", "community-update", "book-signing", "thoughts-from",
    "we-love", "wine-tasting", "perfect-mothers-day", "christmas-hampers", "raises-",
    "opening", "coming-to", "awards", "competition", "shortlisted", "partnership",
    "meals-donated", "from-venice-to-istanbul",
)


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]

    # Raiz antiga de receita: /recipe-<...>-from-rick-steins-<livro>/
    if len(partes) == 1:
        slug = partes[0].lower()
        return slug.startswith("recipe-") and not slug.isdigit()

    # Receita-blog: exatamente /blog/<slug>/  (exclui /blog/ , /blog/page/2/ , feeds)
    if len(partes) == 2 and partes[0] == "blog":
        slug = partes[1].lower()
        if slug in ("page", "feed") or slug.isdigit():
            return False
        if any(t in slug for t in _PALAVRAS_NAO_RECEITA):
            return False
        return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))

    return False


def coletar(limite: int) -> list[dict]:
    # Listagem (sem sitemap só de receitas): cada página da categoria linka ~9 receitas.
    # NÃO usamos coletar_por_listagem porque o texto do link é um botão genérico ("READ MORE")
    # — daria um título inútil. Aqui derivamos o título do slug (humanizar_slug), que é o NOME
    # da receita (rótulo), não o conteúdo (Princípio III).
    vistos = set()
    registros: list[dict] = []
    for lst in URLS_LISTAGEM:
        if len(registros) >= limite:
            break
        try:
            html = base.get(lst).text
        except base.BloqueioError:
            raise
        except Exception:
            continue  # página de paginação inexistente (404) → ignora
        for href, _texto in base.extrair_links(html, lst):
            if len(registros) >= limite:
                break
            href = href.split("#")[0].split("?")[0].rstrip("/")
            if href in vistos or not _e_receita(href):
                continue
            vistos.add(href)
            r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(href), href)
            if base.registro_valido(r):
                registros.append(r)
    return registros
