# Quickstart — Fase 3 — Ampliação de cobertura

**Feature**: 003-cobertura-chefs · **Date**: 2026-06-05

Mesmo ambiente da Fase 2 (já instalado): `requests`, `beautifulsoup4`, `lxml`, `playwright`
+ Chromium. Sem novas dependências.

## Rodar a coleta completa

```bash
cd /Users/infoprice/cookAlaRoulette
source .venv/bin/activate        # se usou venv
python orquestrador.py           # teto ~50/site, todos os adaptadores registrados
python orquestrador.py --limite 20   # rodada mais curta
```

Ao final: relatório por site + `data/receitas.json` (re)gravado. Com 38 sites, a rodada
pode levar **vários minutos** (rede + Playwright nos bloqueados). Timeout por adaptador
evita travar num site lento.

## Verificar a cobertura (SC-001)

```bash
python3 -c "import json;from collections import Counter; d=json.load(open('data/receitas.json')); \
print('receitas:',len(d),'| chefs:',len({r['chef'] for r in d}),'| sites:',len({r['site'] for r in d}))"
python3 tests/test_scrapers.py    # helpers puros (sem rede)
```

Meta: ≥25 chefs de ≥18 países, 0 duplicatas, URLs vivas.

## Adicionar um Chef (Princípio VIII)

1. Criar `scrapers/<site>.py` declarando `CHEF`, `SITE`, `TECNICAS`, e `coletar(limite)`
   usando um dos helpers de `base.py` (sitemap / sitemap-browser / listagem) + o filtro de
   URL daquele site.
2. Registrar o módulo na lista `ADAPTADORES` do `orquestrador.py`.
3. Rodar e conferir no relatório. Nada mais muda.

## Re-indexação (FR-011)

Manual sob demanda: rode `python orquestrador.py` quando quiser atualizar a curadoria.

**Como agendar no futuro** (não implementado nesta fase) — ex.: cron mensal:

```cron
0 4 1 * *  cd /Users/infoprice/cookAlaRoulette && .venv/bin/python orquestrador.py >> scraper.log 2>&1
```

## Frontend (intocado — Princípio IV)

Nada muda no frontend. Após a coleta, `python3 -m http.server 8000` e abrir
`http://localhost:8000/` — a roleta sorteia sobre a curadoria ampliada.
