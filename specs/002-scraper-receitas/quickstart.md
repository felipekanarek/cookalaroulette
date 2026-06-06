# Quickstart — Fase 2 — Scraper

**Feature**: 002-scraper-receitas · **Date**: 2026-06-05

Como preparar o ambiente, rodar o scraper e validar a saída. O scraper é Python; o frontend
(Fase 1) continua intocado e apenas lê o `data/receitas.json` que o scraper gera.

## Preparar o ambiente Python

```bash
cd /Users/infoprice/cookAlaRoulette
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium   # navegador real p/ sites com JS/bloqueio
```

> `.venv/` é ambiente local — não faz parte do produto. O frontend não depende de nada disso.

## Rodar a coleta

```bash
python orquestrador.py            # teto padrão ~50/site
python orquestrador.py --limite 20   # teto menor para um teste rápido
```

Ao final, o orquestrador imprime o **relatório por site** (técnica usada, coletadas,
duplicatas removidas, URLs mortas descartadas, status) e (re)grava `data/receitas.json`.

## Validar a saída

```bash
# É um array de {chef, site, titulo, url}? Quantas receitas e de quais chefs?
python3 -c "import json; d=json.load(open('data/receitas.json')); print(len(d), sorted({r['chef'] for r in d}))"

# Helpers puros (validação, dedup, normalização, filtro de URL):
python tests/test_orquestrador.py
```

Critérios de aceite (spec): ≥30 receitas de ≥3 sites (SC-001), 100% conformes (SC-002),
0 duplicatas (SC-003), ≥90% das URLs vivas (SC-004), site bloqueado não zera os demais
(SC-005).

## Conferir que o frontend continua funcionando (separação — Princípio IV)

```bash
python3 -m http.server 8000     # servir a raiz
# abrir http://localhost:8000/ e clicar — agora sorteia sobre os dados coletados
```

Nenhum arquivo do frontend foi alterado; ele só passou a ler um `receitas.json` gerado.

## Adicionar um novo site (Fase 3, por adição)

Criar `scrapers/<novo_site>.py` implementando o contrato
([contracts/adapter-contract.md](./contracts/adapter-contract.md)) e registrá-lo na lista de
adaptadores do `orquestrador.py`. Nada mais muda (Princípio VIII).
