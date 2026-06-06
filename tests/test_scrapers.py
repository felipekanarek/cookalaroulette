#!/usr/bin/env python3
"""Testes dos helpers PUROS novos da Fase 3 (sem rede).
Rodar: python tests/test_scrapers.py    Compatível com Python 3.9.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import base, panelinha, seriouseats

_passou = 0


def check(c, m=""):
    assert c, m


def teste(nome, fn):
    global _passou
    fn(); _passou += 1
    print("  ✓ " + nome)


def main():
    print("scrapers — helpers puros (Fase 3)")

    HTML = '''
      <html><body>
        <a href="/receita/bolo-de-laranja">Bolo de Laranja</a>
        <a href="https://www.panelinha.com.br/receita/nhoque">Nhoque</a>
        <a href="/sobre">Sobre</a>
        <a href="/receitas/tipo/doce">Doces</a>
      </body></html>
    '''

    teste("extrair_links resolve URLs absolutas e captura o texto", lambda: (lambda links: (
        check(("https://www.panelinha.com.br/receita/bolo-de-laranja", "Bolo de Laranja") in links),
        check(any(h == "https://www.panelinha.com.br/receita/nhoque" for h, _ in links)),
    ))(base.extrair_links(HTML, "https://www.panelinha.com.br/")))

    teste("panelinha._e_receita aceita /receita/<slug>, rejeita listagem/sobre", lambda: (
        check(panelinha._e_receita("https://www.panelinha.com.br/receita/bolo-de-laranja")),
        check(not panelinha._e_receita("https://www.panelinha.com.br/receitas/tipo/doce")),
        check(not panelinha._e_receita("https://www.panelinha.com.br/sobre")),
    ))

    teste("seriouseats._e_receita aceita slug-recipe-<id>, rejeita artigo", lambda: (
        check(seriouseats._e_receita("https://www.seriouseats.com/the-best-chili-recipe-5118930")),
        check(not seriouseats._e_receita("https://www.seriouseats.com/how-to-sharpen-knives")),
        check(not seriouseats._e_receita("https://www.seriouseats.com/news/2023/01/something-123456")),
    ))

    teste("humanizar_slug lida com slug acentuado/multilíngue", lambda: check(
        base.humanizar_slug("https://x.com/recipe/bibimbap-set") == "Bibimbap Set"
    ))

    print("\n" + str(_passou) + " testes passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
