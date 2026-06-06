"""Adaptador: Joanna / Kwestia Smaku (Polônia) — site Drupal 7, via crawl de listagem.

Particularidades descobertas sondando o site (justificam o desvio dos helpers padrão):

1. NÃO é WordPress/Yoast: é Drupal 7. `/sitemap.xml` (e variantes) devolve a página
   "Strona nie znaleziona" (404 HTML), e o robots.txt não declara nenhum `Sitemap:`.
   Logo, não há sitemap utilizável → coleta por listagem (FR-002), não por sitemap.

2. O servidor bloqueia pelo User-Agent: com o UA do bot (base.USER_AGENT) a conexão é
   derrubada (ConnectionReset) e o Chromium do helper de navegador recebe
   ERR_HTTP2_PROTOCOL_ERROR. Com um UA de navegador comum o `requests` responde 200.
   Por isso este adaptador faz GET próprio com UA de navegador (os helpers de browser/
   sitemap de base.py usam o UA do bot e seriam barrados). Reusa só os helpers PUROS de
   base.py (extrair_links, humanizar_slug, fazer_registro, registro_valido).

3. Estrutura de URLs:
   - Receita individual: caminho termina em `/przepis.html` (singular)
     ex.: /dania_dla_dwojga/ryz/biryani_z_dynia_grzybami/przepis.html
   - Páginas de listagem/categoria: `/przepisy/<slug>` (tags, ex.: /przepisy/bigos),
     `.../przepisy.html` (plural) e outros `.html` de categoria — NÃO são receitas.
   A home e a página /przepisy listam ~140 tags `/przepisy/<slug>`; cada tag lista
   várias receitas `/przepis.html`. As páginas de receita não linkam outras receitas
   (BFS não propaga), então partimos das listagens de tags.

Coleta APENAS localização (chef/site/titulo/url), nunca conteúdo (Princípio III).
Compatível com Python 3.9.
"""
from __future__ import annotations

import time
from urllib.parse import urljoin, urlparse

import requests

from . import base

CHEF = "Joanna"
SITE = "kwestiasmaku.com"
TECNICAS = ["crawl"]
BASE_URL = "https://www.kwestiasmaku.com"

# Páginas-semente que enumeram as tags de receita (/przepisy/<slug>).
SEEDS = [BASE_URL + "/", BASE_URL + "/przepisy"]

# UA de navegador: o site derruba a conexão para o UA do bot (ver docstring).
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}
_PAUSA = 0.5  # cortesia entre requisições


def _get(url: str, *, timeout: int = 20, tentativas: int = 3) -> str:
    """GET educado com UA de navegador; devolve HTML (ou '' em falha). 403/429 → BloqueioError."""
    ultimo_erro = None
    for n in range(tentativas):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True)
        except requests.RequestException as e:
            ultimo_erro = e
            time.sleep(_PAUSA * (n + 1))
            continue
        if resp.status_code in (403, 429):
            raise base.BloqueioError(f"{resp.status_code} em {url}")
        if resp.status_code >= 500:
            ultimo_erro = requests.HTTPError(f"{resp.status_code} em {url}")
            time.sleep(_PAUSA * (n + 1))
            continue
        if resp.status_code >= 400:
            return ""  # 404 etc. — segue sem essa página
        if not resp.encoding or resp.encoding.lower() in ("iso-8859-1", "latin-1"):
            resp.encoding = resp.apparent_encoding or "utf-8"
        time.sleep(_PAUSA)
        return resp.text
    if ultimo_erro:
        raise ultimo_erro
    return ""


def _titulo(url: str) -> str:
    """Título legível a partir do penúltimo segmento (o último é sempre 'przepis.html').

    ex.: .../desery/ciasta/ciasto_marchewkowe/przepis.html -> 'Ciasto Marchewkowe'.
    Isso é o NOME (rótulo) da receita, não o conteúdo (Princípio III).
    """
    partes = [s for s in urlparse(url).path.split("/") if s]
    if len(partes) >= 2:
        return base.humanizar_slug("/" + partes[-2])
    return base.humanizar_slug(url)


def _e_receita(url: str) -> bool:
    """Receita individual: mesmo host e caminho terminando em /przepis.html (singular)."""
    p = urlparse(url)
    if "kwestiasmaku.com" not in p.netloc:
        return False
    return p.path.lower().rstrip("/").endswith("/przepis.html")


def _e_listagem_de_tag(url: str) -> bool:
    """Página de tag que lista receitas: /przepisy/<slug> (sem .html, um segmento após przepisy)."""
    p = urlparse(url)
    if "kwestiasmaku.com" not in p.netloc:
        return False
    partes = [s for s in p.path.split("/") if s]
    return len(partes) == 2 and partes[0] == "przepisy" and not partes[1].endswith(".html")


def coletar(limite: int) -> list[dict]:
    """Coleta receitas por listagem: descobre as tags /przepisy/<slug> nas sementes e
    visita cada uma colhendo os links /przepis.html, até atingir `limite`."""
    vistos: set = set()
    registros: list[dict] = []

    # 1) Descobre as páginas de listagem (tags) a partir das sementes.
    listagens: list[str] = []
    listagens_set: set = set()
    for seed in SEEDS:
        if len(registros) >= limite:
            return registros
        html = _get(seed)
        if not html:
            continue
        for href, _texto in base.extrair_links(html, seed):
            href = href.split("#")[0].split("?")[0]
            # receitas já presentes nas próprias sementes
            if _e_receita(href) and href not in vistos:
                vistos.add(href)
                r = base.fazer_registro(CHEF, SITE, _titulo(href), href)
                if base.registro_valido(r):
                    registros.append(r)
                    if len(registros) >= limite:
                        return registros
            elif _e_listagem_de_tag(href) and href not in listagens_set:
                listagens_set.add(href)
                listagens.append(href)

    # 2) Visita cada listagem de tag e colhe as receitas (/przepis.html).
    for lst in listagens:
        if len(registros) >= limite:
            break
        html = _get(lst)
        if not html:
            continue
        for href, _texto in base.extrair_links(html, lst):
            if len(registros) >= limite:
                break
            href = href.split("#")[0].split("?")[0]
            if not _e_receita(href) or href in vistos:
                continue
            vistos.add(href)
            r = base.fazer_registro(CHEF, SITE, _titulo(href), href)
            if base.registro_valido(r):
                registros.append(r)

    return registros
