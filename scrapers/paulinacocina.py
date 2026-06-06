"""Adaptador: Paulina Cocina (Argentina) — via sitemap (Yoast).

O sitemap raiz é um índice Yoast com vários sub-sitemaps (post/page/category/tag/author/
video/restaurante). As receitas (e posts de comida) vivem nos `post-sitemap{N}.xml`, sempre
no padrão de URL `/slug/<id-numérico>` (ex.: /flan-casero-clasico/13997). Esse ID numérico
é o marcador que separa POSTS de páginas institucionais, categorias e tags — então filtramos
exigindo-o (sub_filtro de posts + marcador na URL).

Particularidades que justificam um coletor próprio em vez de `coletar_por_sitemap`:
- O título precisa vir do PRIMEIRO segmento (o slug), não do último (o ID numérico). O
  helper genérico usa `humanizar_slug` (último segmento), que aqui devolveria só o número.

Ressalva: é um blog grande; entre os posts há explicadores de ingrediente/utensílio
("queso-brie", "molinillo-de-cafe", "creme-fraiche"). Eles compartilham o mesmo padrão
`/slug/id` das receitas e não são separáveis só pela URL — então alguns entram na amostra.
Coletamos APENAS localização (chef/site/título/url), nunca conteúdo (Princípio III).
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

from . import base

CHEF = "Paulina Cocina"
SITE = "paulinacocina.net"
TECNICAS = ["sitemap"]
BASE_URL = "https://www.paulinacocina.net"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page-/category-/post_tag-/author-/video-/restaurante-sitemap.
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


def _e_receita(url: str) -> bool:
    """Receita/post de comida = URL no padrão `/slug/<id-numérico>` do domínio."""
    p = urlparse(url)
    if SITE not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 2:
        return False
    slug, ident = partes
    if not ident.isdigit():  # o ID numérico é o marcador de post (exclui páginas/taxonomias)
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))  # kebab-case


def _titulo(url: str) -> str:
    """Título legível a partir do slug (PRIMEIRO segmento), descartando o ID numérico."""
    partes = [s for s in urlparse(url).path.split("/") if s]
    slug = partes[0] if partes else ""
    slug = re.sub(r"[-_]+", " ", slug).strip()
    return slug.title() if slug else "(sem título)"


def coletar(limite: int) -> list[dict]:
    vistos = set()
    registros: list[dict] = []
    for sitemap in base.descobrir_sitemaps(BASE_URL):
        for url in base.iter_urls_sitemap(sitemap, sub_filtro=_sub_sitemap_de_posts):
            if len(registros) >= limite:
                return registros
            if url in vistos or not _e_receita(url):
                continue
            vistos.add(url)
            r = base.fazer_registro(CHEF, SITE, _titulo(url), url)
            if base.registro_valido(r):
                registros.append(r)
    return registros
