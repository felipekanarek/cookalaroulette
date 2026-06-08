#!/usr/bin/env python3
"""Testes dos helpers PUROS do scraper (sem rede). Rodar: python tests/test_orquestrador.py

Cobre: validação de registro (contrato), normalização de URL, deduplicação e os filtros
de URL de receita de cada adaptador. Os adaptadores em si dependem de rede e são
validados manualmente (quickstart).
Compatível com Python 3.9.
"""
import os
import sys

# permite importar os módulos da raiz do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers import base, recipetineats, panelinha, jamieoliver, seriouseats, maangchi
import orquestrador as orq

_passou = 0


def check(cond, msg=""):
    assert cond, msg


def teste(nome, fn):
    global _passou
    fn()
    _passou += 1
    print("  ✓ " + nome)


def main():
    print("orquestrador / base — helpers puros")

    teste("registro_valido aceita registro completo", lambda: check(
        base.registro_valido({"chef": "X", "site": "s.com", "titulo": "T", "url": "https://s.com/r"})
    ))

    teste("registro_valido rejeita campos vazios / url ruim", lambda: (
        check(not base.registro_valido({"chef": "", "site": "s", "titulo": "t", "url": "https://s/r"})),
        check(not base.registro_valido({"chef": "X", "site": "s", "titulo": "t", "url": "ftp://x"})),
        check(not base.registro_valido({"chef": "X", "site": "s", "titulo": "t", "url": ""})),
    ))

    teste("normalizar_url remove barra final, fragmento, query e baixa o host", lambda: check(
        orq.normalizar_url("HTTPS://WWW.Site.com/Receita/Bolo/?share=facebook#x")
            == "https://www.site.com/Receita/Bolo"
    ))

    teste("deduplicar remove mesma URL normalizada (barra/share/utm)", lambda: (lambda res: check(
        len(res[0]) == 1 and res[1] == 3
    ))(orq.deduplicar([
        {"chef": "a", "site": "s", "titulo": "t", "url": "https://s.com/r/"},
        {"chef": "a", "site": "s", "titulo": "t", "url": "https://s.com/r"},
        {"chef": "a", "site": "s", "titulo": "t", "url": "https://s.com/r/?share=facebook"},
        {"chef": "a", "site": "s", "titulo": "t", "url": "https://s.com/r/?utm_source=x"},
    ])))

    teste("humanizar_slug deriva título do slug", lambda: check(
        base.humanizar_slug("https://www.recipetineats.com/butter-chicken/") == "Butter Chicken"
    ))

    teste("recipetineats: aceita slug de raiz, rejeita seções", lambda: (
        check(recipetineats._e_receita("https://www.recipetineats.com/butter-chicken/")),
        check(not recipetineats._e_receita("https://www.recipetineats.com/recipes/")),
        check(not recipetineats._e_receita("https://www.recipetineats.com/about/")),
        check(not recipetineats._e_receita("https://www.recipetineats.com/a/b/")),
    ))

    teste("panelinha: aceita /receita/<slug>", lambda: (
        check(panelinha._e_receita("https://www.panelinha.com.br/receita/arroz-de-forno")),
        check(not panelinha._e_receita("https://www.panelinha.com.br/receitas")),
        check(not panelinha._e_receita("https://www.panelinha.com.br/receita/cat/x")),
    ))

    teste("jamieoliver: aceita /recipes/<cat>/<slug>/, rejeita categoria", lambda: (
        check(jamieoliver._e_receita("https://www.jamieoliver.com/recipes/pasta-recipes/spaghetti-carbonara/")),
        check(not jamieoliver._e_receita("https://www.jamieoliver.com/recipes/")),
        check(not jamieoliver._e_receita("https://www.jamieoliver.com/recipes/pasta-recipes/")),
    ))

    teste("seriouseats: aceita slug com 'recipe' + id, rejeita artigo", lambda: (
        check(seriouseats._e_receita("https://www.seriouseats.com/the-best-chili-recipe-5118930")),
        check(not seriouseats._e_receita("https://www.seriouseats.com/how-to-sharpen-knives")),
    ))

    teste("maangchi: aceita /recipe/<slug>", lambda: (
        check(maangchi._e_receita("https://www.maangchi.com/recipe/bibimbap")),
        check(not maangchi._e_receita("https://www.maangchi.com/recipes")),
    ))

    print("\n" + str(_passou) + " testes passaram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
