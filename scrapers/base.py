"""base.py — helpers compartilhados pelos adaptadores (Fase 2).

Concentra o que é comum a todos os sites para que cada adaptador seja pequeno e não
repita código nem vaze formato (Princípio V). Coleta APENAS localização de receita
(chef/site/titulo/url) — nunca conteúdo (Princípio III).

Compatível com Python 3.9.
"""
from __future__ import annotations

import gzip
import json
import re
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# User-Agent honesto e identificável (coleta educada, Princípio VII).
USER_AGENT = (
    "CookALaRouletteBot/1.0 (+https://github.com/; projeto de aprendizado de scraping) "
    "Mozilla/5.0 (compatible)"
)
HEADERS = {"User-Agent": USER_AGENT, "Accept": "*/*"}
PAUSA = 0.4  # s entre requisições, por cortesia


class BloqueioError(Exception):
    """Sinaliza que um site bloqueou a coleta (403/429/desafio anti-bot)."""


def get(url: str, *, timeout: int = 15, tentativas: int = 3) -> requests.Response:
    """GET educado, com retry/backoff em erros transitórios.

    Levanta BloqueioError em 403/429 (anti-bot). Levanta requests.HTTPError em 4xx/5xx
    não-transitórios após as tentativas.
    """
    ultimo_erro = None
    for n in range(tentativas):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        except requests.RequestException as e:
            ultimo_erro = e
            time.sleep(PAUSA * (n + 1))
            continue
        if resp.status_code in (403, 429):
            raise BloqueioError(f"{resp.status_code} em {url}")
        if resp.status_code >= 500:
            ultimo_erro = requests.HTTPError(f"{resp.status_code} em {url}")
            time.sleep(PAUSA * (n + 1))
            continue
        resp.raise_for_status()
        # requests assume ISO-8859-1 quando o header não declara charset → corrige mojibake
        if not resp.encoding or resp.encoding.lower() in ("iso-8859-1", "latin-1"):
            resp.encoding = resp.apparent_encoding or "utf-8"
        time.sleep(PAUSA)
        return resp
    raise ultimo_erro if ultimo_erro else requests.HTTPError(f"falha em {url}")


def _conteudo(resp: requests.Response) -> bytes:
    """Descomprime sitemaps .gz quando necessário."""
    if resp.url.endswith(".gz") or resp.headers.get("Content-Type", "").endswith("gzip"):
        try:
            return gzip.decompress(resp.content)
        except OSError:
            return resp.content
    return resp.content


def _localname(tag: str) -> str:
    return tag.split("}")[-1]  # remove namespace {http://...}loc -> loc


def descobrir_sitemaps(base_url: str) -> list[str]:
    """Acha sitemaps via robots.txt (linhas 'Sitemap:'); fallback para /sitemap.xml."""
    encontrados: list[str] = []
    try:
        robots = get(urljoin(base_url, "/robots.txt"))
        for linha in robots.text.splitlines():
            if linha.lower().startswith("sitemap:"):
                valor = linha.split(":", 1)[1].strip()
                encontrados.append(urljoin(base_url, valor))  # resolve Sitemap: relativo
    except BloqueioError:
        raise  # bloqueio deve propagar (não mascarar como "sem sitemap")
    except Exception:
        pass
    if not encontrados:
        encontrados.append(urljoin(base_url, "/sitemap.xml"))
    return encontrados


def iter_urls_sitemap(sitemap_url, *, sub_filtro=None, profundidade=0, max_prof=3):
    """Gera URLs (<loc>) de um sitemap, recursando em índices aninhados.

    `sub_filtro(url)->bool`: se dado, no índice só recursa nos sub-sitemaps aprovados
    (ex.: apenas sitemaps de "posts"). BloqueioError propaga (não é silenciado).
    """
    if profundidade > max_prof:
        return
    resp = get(sitemap_url)  # BloqueioError propaga
    try:
        raiz = ET.fromstring(_conteudo(resp))
    except ET.ParseError:
        return
    tag = _localname(raiz.tag)
    if tag == "sitemapindex":
        for sm in raiz:
            loc = next((c for c in sm if _localname(c.tag) == "loc"), None)
            if loc is not None and loc.text:
                sub = loc.text.strip()
                if sub_filtro is None or sub_filtro(sub):
                    yield from iter_urls_sitemap(sub, sub_filtro=sub_filtro,
                                                 profundidade=profundidade + 1, max_prof=max_prof)
    else:  # urlset
        for u in raiz:
            loc = next((c for c in u if _localname(c.tag) == "loc"), None)
            if loc is not None and loc.text:
                yield loc.text.strip()


def humanizar_slug(url: str) -> str:
    """Deriva um título legível do último segmento do caminho da URL.

    Ex.: https://site.com/butter-chicken/ -> 'Butter Chicken'.
    Isso é o NOME da receita (rótulo), não o conteúdo (Princípio III).
    """
    caminho = urlparse(url).path.rstrip("/")
    slug = caminho.split("/")[-1] if caminho else ""
    slug = re.sub(r"\.\w+$", "", slug)              # remove extensão
    slug = re.sub(r"[-_]+", " ", slug).strip()
    slug = re.sub(r"\s+\d+$", "", slug).strip()     # remove id numérico final (ex.: "... recipe 8665080")
    return slug.title() if slug else "(sem título)"


def fazer_registro(chef: str, site: str, titulo: str, url: str) -> dict:
    return {"chef": chef, "site": site, "titulo": titulo, "url": url}


def registro_valido(r: dict) -> bool:
    """Valida contra o contrato {chef, site, titulo, url} (Fase 1 schema)."""
    if not isinstance(r, dict):
        return False
    for campo in ("chef", "site", "titulo", "url"):
        if not isinstance(r.get(campo), str) or not r[campo].strip():
            return False
    return bool(re.match(r"^https?://", r["url"].strip()))


def coletar_por_sitemap(base_url, chef, site, url_e_receita, limite, *, sub_filtro=None):
    """Coleta receitas via sitemap: itera <loc>, filtra com `url_e_receita(url)->bool`,
    monta registros (título derivado do slug) e para ao atingir `limite`.

    `url_e_receita`: predicado que decide se uma URL é de receita individual (FR-008).
    `sub_filtro`: opcional, limita quais sub-sitemaps seguir num índice (ex.: só "posts").
    """
    vistos = set()
    registros: list[dict] = []
    for sitemap in descobrir_sitemaps(base_url):
        for url in iter_urls_sitemap(sitemap, sub_filtro=sub_filtro):
            if len(registros) >= limite:
                return registros
            if url in vistos or not url_e_receita(url):
                continue
            vistos.add(url)
            r = fazer_registro(chef, site, humanizar_slug(url), url)
            if registro_valido(r):
                registros.append(r)
    return registros


# ---- Helper PURO: extrair links de uma página de listagem -------------------------

def extrair_links(html: str, base_url: str):
    """Extrai (url_absoluta, texto) de todos os <a href> de um HTML. Puro (testável)."""
    sopa = BeautifulSoup(html, "html.parser")
    out = []
    for a in sopa.find_all("a", href=True):
        href = urljoin(base_url, a["href"].strip())
        texto = " ".join(a.get_text(" ", strip=True).split())
        out.append((href, texto))
    return out


# ---- Coleta via crawl de listagem (sites SEM sitemap) — FR-002 --------------------

def coletar_por_listagem(urls_listagem, chef, site, url_e_receita, limite, *, usar_browser=False):
    """Coleta receitas a partir de páginas de listagem (sem sitemap).

    requests+BS4 por padrão; Playwright (corpo renderizado) se `usar_browser=True` ou se a
    página vier praticamente sem links (provável conteúdo via JS). `url_e_receita(url)->bool`
    filtra receitas individuais. Título = texto do link (se houver) ou slug.
    """
    if isinstance(urls_listagem, str):
        urls_listagem = [urls_listagem]
    vistos = set()
    registros = []

    def processa(html, base):
        for href, texto in extrair_links(html, base):
            if len(registros) >= limite:
                return
            if href in vistos or not url_e_receita(href):
                continue
            vistos.add(href)
            titulo = texto if texto else humanizar_slug(href)
            r = fazer_registro(chef, site, titulo, href)
            if registro_valido(r):
                registros.append(r)

    for lst in urls_listagem:
        if len(registros) >= limite:
            break
        html = None
        if not usar_browser:
            try:
                html = get(lst).text
            except BloqueioError:
                usar_browser = True  # bloqueou → tenta navegador no restante
        if usar_browser or not html or html.count("<a") < 5:
            html = _html_via_browser(lst)
        if html:
            processa(html, lst)
    return registros


def coletar_por_crawl(seeds, chef, site, url_e_receita, limite, *, max_paginas=40):
    """Crawl BFS para sites sem sitemap nem listagem indexável: parte de páginas-semente,
    segue os links de receita que cada página revela (ex.: "receitas relacionadas") e
    descobre o catálogo em largura. Para ao atingir `limite` ou `max_paginas` visitadas.

    `url_e_receita(url)->bool` decide o que é receita. Título = texto do link ou slug.
    """
    if isinstance(seeds, str):
        seeds = [seeds]
    fila = list(seeds)
    enfileirados = set(seeds)
    visitadas = set()
    registros, reg_urls = [], set()

    while fila and len(registros) < limite and len(visitadas) < max_paginas:
        pagina = fila.pop(0)
        if pagina in visitadas:
            continue
        visitadas.add(pagina)
        try:
            html = get(pagina).text
        except BloqueioError:
            raise
        except Exception:
            continue
        for href, texto in extrair_links(html, pagina):
            href = href.split("#")[0].rstrip("/")
            if not url_e_receita(href):
                continue
            if href not in reg_urls and len(registros) < limite:
                titulo = texto if texto else humanizar_slug(href)
                r = fazer_registro(chef, site, titulo, href)
                if registro_valido(r):
                    registros.append(r)
                    reg_urls.add(href)
            if href not in enfileirados:        # explora a partir dessa receita também
                fila.append(href)
                enfileirados.add(href)
    return registros


# ---- Coleta de sitemap via NAVEGADOR (sites bloqueados) — generaliza a Maangchi ----

def _html_via_browser(url: str) -> str:
    """Busca o HTML/markup renderizado de uma URL via Chromium (passa por muitos bloqueios)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise BloqueioError("Playwright indisponível") from e
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=True)
        pg = nav.new_page(user_agent=USER_AGENT)
        try:
            resp = pg.goto(url, wait_until="domcontentloaded", timeout=25000)
            if resp is None or resp.status in (403, 429):
                raise BloqueioError(f"navegador bloqueado ({resp.status if resp else '??'}) em {url}")
            return pg.content()
        finally:
            nav.close()


def coletar_por_sitemap_browser(base_url, chef, site, url_e_receita, limite, *, sub_filtro=None):
    """Como coletar_por_sitemap, mas buscando os sitemaps via Chromium pelo CORPO BRUTO da
    resposta (resp.text(), não o DOM — o Chromium renderiza XML como árvore visual).
    Para sites que bloqueiam o cliente HTTP comum mas liberam o navegador. Recursa índices."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise BloqueioError("Playwright indisponível") from e

    vistos = set()
    registros = []
    with sync_playwright() as pw:
        nav = pw.chromium.launch(headless=True)

        def locs_de(url):
            # aba NOVA por fetch: reusar a mesma aba faz resp.text() voltar vazio em
            # sitemaps grandes (bug observado em post-sitemaps de ~2-3 MB).
            p = nav.new_page(user_agent=USER_AGENT)
            try:
                resp = p.goto(url, wait_until="commit", timeout=25000)
                if resp is None or resp.status in (403, 429):
                    raise BloqueioError(f"navegador bloqueado ({resp.status if resp else '??'}) em {url}")
                return re.findall(r"<loc>(.*?)</loc>", resp.text())
            finally:
                p.close()

        try:
            raiz = locs_de(urljoin(base_url, "/sitemap.xml"))
            sub = [u for u in raiz if u.endswith(".xml") and (sub_filtro is None or sub_filtro(u))]
            paginas = [] if sub else [u for u in raiz if not u.endswith(".xml")]
            for sm in sub:
                if len(registros) >= limite:
                    break
                try:
                    for u in locs_de(sm):
                        if u.endswith(".xml"):
                            continue
                        if u in vistos or not url_e_receita(u):
                            continue
                        vistos.add(u)
                        r = fazer_registro(chef, site, humanizar_slug(u), u)
                        if registro_valido(r):
                            registros.append(r)
                        if len(registros) >= limite:
                            break
                except BloqueioError:
                    continue
            for u in paginas:  # caso o sitemap raiz já fosse um urlset
                if len(registros) >= limite:
                    break
                if u in vistos or not url_e_receita(u):
                    continue
                vistos.add(u)
                r = fazer_registro(chef, site, humanizar_slug(u), u)
                if registro_valido(r):
                    registros.append(r)
        finally:
            nav.close()
    return registros


# ---- Descoberta via Internet Archive (Wayback CDX) — para sites atrás de Cloudflare -------

def coletar_por_wayback(dominio, chef, site, url_e_receita, limite, *, cdx_filtro=None):
    """Descobre URLs de receita pelo Internet Archive (API CDX), SEM tocar no site.

    Útil quando o site bloqueia bots (Cloudflare) mas a página existe para humanos: o app
    só precisa da URL para redirecionar, e a verificação trata 403 como "existe". Não
    contornamos a proteção — apenas usamos uma fonte pública de descoberta. As URLs são as
    reais (vivas); o título vem do slug.

    `cdx_filtro`: regex opcional aplicada no servidor (filter=original:<regex>) para reduzir
    a resposta; `url_e_receita` faz o filtro final localmente.
    """
    # limit baixo o suficiente p/ o CDX não varrer o índice inteiro (domínios grandes dão
    # timeout com limit alto), mas com folga p/ dedup de variantes ?query.
    cdx = ("http://web.archive.org/cdx/search/cdx?url=" + dominio +
           "&matchType=domain&collapse=urlkey&output=json&fl=original&limit=" +
           str(max(500, limite * 20)))
    if cdx_filtro:
        cdx += "&filter=original:" + cdx_filtro
    # O CDX do archive.org tem rate-limit e pode dar timeout em domínios grandes →
    # retry com backoff (evita perder o site quando vários adaptadores wayback rodam juntos).
    linhas = None
    for tentativa in range(4):
        try:
            resp = requests.get(cdx, headers=HEADERS, timeout=120)
            resp.raise_for_status()
            linhas = resp.json()
            break
        except Exception:
            time.sleep(4 * (tentativa + 1))
    if not linhas:
        return []
    vistos = set()
    registros = []
    for linha in linhas[1:]:  # pula o cabeçalho
        bruta = linha[0] if isinstance(linha, list) else linha
        url = bruta.split("#")[0].split("?")[0].rstrip("/")  # remove query/fragmento
        if url.startswith("http://"):
            url = "https://" + url[len("http://"):]          # normaliza esquema (evita http/https dup)
        if url in vistos or not url_e_receita(url):
            continue
        vistos.add(url)
        r = fazer_registro(chef, site, humanizar_slug(url), url)
        if registro_valido(r):
            registros.append(r)
        if len(registros) >= limite:
            break
    return registros
