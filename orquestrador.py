#!/usr/bin/env python3
"""orquestrador.py — Fase 2 do Cook à la Roulette.

Chama os adaptadores de cada site, consolida os registros no contrato
{chef, site, titulo, url}, deduplica, descarta URLs mortas, grava data/receitas.json
de forma atômica e imprime um relatório por site.

É o ÚNICO componente que escreve data/receitas.json. NÃO toca o frontend (Princípio IV).
Coleta apenas localização de receita — nunca conteúdo (Princípio III).

Uso:  python orquestrador.py [--limite N]   (padrão N=50)
Compatível com Python 3.9.
"""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, urlunparse

import requests

from scrapers import (base, recipetineats, panelinha, jamieoliver, seriouseats, maangchi,
                      patijinich, natashaskitchen, laylita, ceciliatupac, paulinacocina,
                      justonecookbook, akispetretzikis, vincenzosplate, thespanishchef,
                      kwestiasmaku, donalskehan, northwildkitchen, trinehahnemann,
                      callmecupcake, kitchenbutterfly, simplydelicious, thewoksoflife,
                      sanjeevkapoor, danangcuisine, belagil, nigella, ottolenghi,
                      smittenkitchen, adamliaw, misya, davidlebovitz, hotthaikitchen)
# Serious Eats, David Lebovitz e Hot Thai Kitchen estão atrás do Cloudflare → descobertos
# via Internet Archive (Wayback), sem tocar no site. NÃO registrado: zoesghana (domínio morto).

# Adaptadores registrados. Adicionar um site = importar e incluir aqui (Princípio VIII).
ADAPTADORES = [recipetineats, panelinha, jamieoliver, seriouseats, maangchi,
               patijinich, natashaskitchen, laylita, ceciliatupac, paulinacocina,
               justonecookbook, akispetretzikis, vincenzosplate, thespanishchef,
               kwestiasmaku, donalskehan, northwildkitchen, trinehahnemann,
               callmecupcake, kitchenbutterfly, simplydelicious, thewoksoflife,
               sanjeevkapoor, danangcuisine, belagil, nigella, ottolenghi,
               smittenkitchen, adamliaw, misya, davidlebovitz, hotthaikitchen]

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "data", "receitas.json")
TETO_PADRAO = 50


# ---- helpers puros (testados em tests/test_orquestrador.py) -----------------------

def normalizar_url(url: str) -> str:
    """Normaliza para deduplicação: esquema/host minúsculos, sem fragmento, sem barra final."""
    p = urlparse(url.strip())
    caminho = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower(), p.netloc.lower(), caminho, "", p.query, ""))


def deduplicar(registros):
    """Remove registros com a mesma URL normalizada (mantém o primeiro). FR-007.
    Retorna (lista_sem_duplicatas, qtd_removida)."""
    vistos = set()
    saida = []
    for r in registros:
        chave = normalizar_url(r["url"])
        if chave in vistos:
            continue
        vistos.add(chave)
        saida.append(r)
    return saida, len(registros) - len(saida)


# ---- verificação de URLs vivas (rede) --------------------------------------------

# Códigos que indicam que a página EXISTE (mesmo que bloqueie bots): tratamos como viva,
# pois o app redireciona um humano (cujo navegador acessa normalmente). Só 404/410/5xx,
# erros de rede etc. são considerados link morto.
_EXISTE_MAS_RESTRITO = {401, 403, 429}


# UA de navegador para a verificação (alguns sites recusam o UA de bot e derrubam a conexão,
# mas a página existe para um humano — ex.: kwestiasmaku.com).
_UA_NAVEGADOR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def url_viva(url: str, timeout: int = 10) -> bool:
    """True se a URL resolve (2xx) ou existe mas restringe bots (401/403/429). FR-015.
    Tenta o UA de bot e, se falhar/recusar, reusa um UA de navegador (sites que barram bots
    mas servem humanos). HEAD primeiro; GET quando o servidor recusa HEAD (405)."""
    for headers in (base.HEADERS, _UA_NAVEGADOR):
        try:
            r = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
            if r.status_code == 405:
                r = requests.get(url, headers=headers, timeout=timeout,
                                 allow_redirects=True, stream=True)
            if (200 <= r.status_code < 300) or r.status_code in _EXISTE_MAS_RESTRITO:
                return True
        except requests.RequestException:
            continue
    return False


def verificar_urls(registros):
    """Mantém só registros com URL viva. Retorna (vivos, qtd_descartada). FR-015."""
    if not registros:
        return [], 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        vivas = list(pool.map(lambda r: url_viva(r["url"]), registros))
    vivos = [r for r, ok in zip(registros, vivas) if ok]
    return vivos, len(registros) - len(vivos)


# ---- gravação atômica -------------------------------------------------------------

def gravar_atomico(caminho: str, registros) -> None:
    """Grava JSON via arquivo temporário + os.replace (nunca deixa arquivo parcial). FR-012."""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(caminho), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, caminho)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# ---- pipeline ---------------------------------------------------------------------

def coletar_tudo(limite: int):
    """Roda cada adaptador; retorna (registros_validos, relatorio_por_site)."""
    registros = []
    relatorio = []
    for ad in ADAPTADORES:
        nome = getattr(ad, "SITE", ad.__name__)
        try:
            brutos = ad.coletar(limite)
            validos = [r for r in brutos if base.registro_valido(r)]
            registros.extend(validos)
            relatorio.append({"site": nome, "chef": getattr(ad, "CHEF", "?"),
                              "tecnica": "/".join(getattr(ad, "TECNICAS", [])),
                              "coletadas": len(validos),
                              "status": "ok" if validos else "sem-receitas"})
        except base.BloqueioError as e:
            relatorio.append({"site": nome, "chef": getattr(ad, "CHEF", "?"),
                              "tecnica": "/".join(getattr(ad, "TECNICAS", [])),
                              "coletadas": 0, "status": f"bloqueado-pulado ({e})"})
        except Exception as e:  # falha isolada não derruba a rodada (FR-009)
            relatorio.append({"site": nome, "chef": getattr(ad, "CHEF", "?"),
                              "tecnica": "/".join(getattr(ad, "TECNICAS", [])),
                              "coletadas": 0, "status": f"erro ({type(e).__name__}: {e})"})
    return registros, relatorio


def imprimir_relatorio(relatorio, dup_removidas, urls_mortas, total_final):
    print("\n" + "=" * 60)
    print("RELATÓRIO DE COLETA — Cook à la Roulette (Fase 2)")
    print("=" * 60)
    for r in relatorio:
        print(f"  {r['site']:<22} {r['coletadas']:>4} receitas  [{r['tecnica']}]  {r['status']}")
    print("-" * 60)
    print(f"  duplicatas removidas : {dup_removidas}")
    print(f"  URLs mortas descartadas: {urls_mortas}")
    print(f"  TOTAL gravado em data/receitas.json: {total_final}")
    print("=" * 60 + "\n")


def main():
    ap = argparse.ArgumentParser(description="Coleta receitas e gera data/receitas.json")
    ap.add_argument("--limite", type=int, default=TETO_PADRAO,
                    help=f"teto de receitas por site (padrão {TETO_PADRAO})")
    args = ap.parse_args()

    print(f"Coletando (teto {args.limite}/site)...")
    registros, relatorio = coletar_tudo(args.limite)

    registros, dup = deduplicar(registros)          # FR-007
    registros, mortas = verificar_urls(registros)   # FR-015

    # Salvaguarda: não sobrescrever o catálogo existente com um resultado vazio
    # (ex.: rodada totalmente bloqueada / sem rede). Preserva o que o frontend já lê.
    if not registros:
        print("\n⚠️  Nenhuma receita coletada — preservando data/receitas.json existente "
              "(nada foi sobrescrito).")
        imprimir_relatorio(relatorio, dup, mortas, total_final=0)
        return 1

    gravar_atomico(SAIDA, registros)                # FR-012
    imprimir_relatorio(relatorio, dup, mortas, len(registros))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
