"""Adaptador: Just One Cookbook (Namiko Chen, Japão) — sitemap com fallback navegador.

O site responde 403 (anti-bot) ao cliente HTTP comum, então tentamos primeiro
`coletar_por_sitemap` e, em BloqueioError, caímos para `coletar_por_sitemap_browser`
(Chromium, corpo bruto do XML). É WordPress/Yoast: o índice em /sitemap.xml lista vários
sub-sitemaps; só seguimos os de POSTS (onde ficam as receitas), evitando
page/category/tag/ingredient/diet/collection-sitemaps (taxonomia e páginas institucionais).

Receitas ficam em slug de raiz: https://www.justonecookbook.com/<slug>/
O post-sitemap também traz glossário de ingredientes e how-tos; filtramos os slugs
obviamente não-receita por uma lista de exclusão (mesma estratégia da RecipeTin Eats).
Coletamos APENAS localização (chef/site/titulo/url), nunca conteúdo (Princípio III).

Nota: o post-sitemap deste site é grande (~2,8 MB). Reaproveitar a MESMA aba do Chromium
para buscar vários sitemaps faz `resp.text()` voltar vazio nesse XML grande; por isso usamos
uma aba NOVA por sitemap (ver `_coletar_browser`), em vez do `coletar_por_sitemap_browser`.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from . import base

CHEF = "Namiko Chen"
SITE = "justonecookbook.com"
TECNICAS = ["sitemap", "playwright"]
BASE_URL = "https://www.justonecookbook.com"


# Só seguimos os sub-sitemaps de POSTS (onde ficam as receitas), evitando
# page/category/tag/joc_ingredient/joc_diet/... (taxonomia, páginas institucionais).
def _sub_sitemap_de_posts(url: str) -> bool:
    return "post-sitemap" in url.lower()


# Slugs de raiz que NÃO são receitas (páginas institucionais e seções do blog).
_NAO_RECEITA = {
    "blog", "about", "about-me", "contact", "privacy-policy", "terms",
    "category", "tag", "subscribe", "shop", "cookbook", "cookbooks",
    "my-account", "search", "newsletter", "faq", "press", "recipes",
    "web-stories", "disclosure", "wprm_print", "membership", "members",
    "gift", "links", "start-here", "resources",
}


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
    # slug em kebab-case (palavras separadas por hífen); exclui underscore e ids puros
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug))


def _coletar_browser(limite: int) -> list[dict]:
    """Fallback via Chromium: lê o índice e cada post-sitemap em ABA NOVA (o XML grande
    volta vazio se a aba for reaproveitada). Recursa só os sub-sitemaps de posts."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise base.BloqueioError("Playwright indisponível") from e

    vistos = set()
    registros: list[dict] = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=True)

        def locs_de(url):
            pg = nav.new_page(user_agent=base.USER_AGENT)
            try:
                resp = pg.goto(url, wait_until="commit", timeout=30000)
                if resp is None or resp.status in (403, 429):
                    raise base.BloqueioError(
                        f"navegador bloqueado ({resp.status if resp else '??'}) em {url}")
                return re.findall(r"<loc>(.*?)</loc>", resp.text())
            finally:
                pg.close()

        try:
            raiz = locs_de(urljoin(BASE_URL, "/sitemap.xml"))
            sub = [u for u in raiz if u.endswith(".xml") and _sub_sitemap_de_posts(u)]
            for sm in sub:
                if len(registros) >= limite:
                    break
                try:
                    locs = locs_de(sm)
                except base.BloqueioError:
                    continue
                for u in locs:
                    if len(registros) >= limite:
                        break
                    if u.endswith(".xml") or u in vistos or not _e_receita(u):
                        continue
                    vistos.add(u)
                    r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(u), u)
                    if base.registro_valido(r):
                        registros.append(r)
        finally:
            nav.close()
    return registros


def coletar(limite: int) -> list[dict]:
    try:
        return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite,
                                        sub_filtro=_sub_sitemap_de_posts)
    except base.BloqueioError:
        return _coletar_browser(limite)
