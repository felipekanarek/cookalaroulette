"""Adaptador: Adam Liaw (Austrália) — via crawl da home (site Next.js, sem sitemap).

adamliaw.com NÃO é WordPress: é um site Next.js cujo /sitemap.xml devolve página de
erro 808. As receitas ficam em https://www.adamliaw.com/recipe/<slug>. A home (HTML do
SSR) já lista ~139 links de receita no markup bruto; as páginas internas de receita são
renderizadas via JS (não revelam novos links ao cliente HTTP), então o catálogo
descoberto vem essencialmente da home — suficiente para o `limite`.

Os textos dos links trazem ruído (ex.: "<30min", "1-4h", rótulos de painel), por isso o
título é derivado do slug (humanizar_slug), não do texto do link. Só localização, nunca
conteúdo (Princípio III).
"""
from __future__ import annotations

from urllib.parse import urlparse

from . import base

CHEF = "Adam Liaw"
SITE = "adamliaw.com"
TECNICAS = ["crawl"]
BASE_URL = "https://www.adamliaw.com"
SEEDS = ["https://www.adamliaw.com/"]


def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if "adamliaw.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    # receitas individuais: /recipe/<slug>
    if len(partes) != 2 or partes[0] != "recipe":
        return False
    return not partes[1].isdigit()


def coletar(limite: int) -> list[dict]:
    """Coleta receitas a partir da home. Título derivado do slug (textos dos links são
    poluídos com metadados de tempo/painel), garantindo rótulos limpos."""
    vistos = set()
    registros: list[dict] = []
    for seed in SEEDS:
        if len(registros) >= limite:
            break
        try:
            html = base.get(seed).text
        except base.BloqueioError:
            raise
        except Exception:
            continue
        for href, _texto in base.extrair_links(html, seed):
            if len(registros) >= limite:
                break
            href = href.split("#")[0].rstrip("/")
            if href in vistos or not _e_receita(href):
                continue
            vistos.add(href)
            r = base.fazer_registro(CHEF, SITE, base.humanizar_slug(href), href)
            if base.registro_valido(r):
                registros.append(r)
    return registros
