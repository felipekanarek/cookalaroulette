# Implementation Plan: Fase 2 — Scraper (indexação automatizada de receitas)

**Branch**: `002-scraper-receitas` | **Date**: 2026-06-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-scraper-receitas/spec.md`

## Summary

Um conjunto de adaptadores Python (um por site) coleta URLs de receitas de 5 sites de
Chefs, cada um usando a técnica mais simples que funcione (sitemap → BeautifulSoup →
Playwright). Um orquestrador chama todos os adaptadores, consolida os registros no
contrato `{chef, site, titulo, url}`, deduplica por URL, **verifica que cada URL resolve**
(descartando as mortas), valida contra o schema, e grava `data/receitas.json` de forma
atômica — emitindo um relatório por site. Coleta **apenas a localização** da receita,
nunca o conteúdo (Princípio III). O frontend não é tocado; ele apenas passa a ler um
`receitas.json` agora gerado automaticamente (Princípio IV).

## Technical Context

**Language/Version**: Python 3.11.
**Primary Dependencies**: `requests` (HTTP com User-Agent realista), `beautifulsoup4` + `lxml`
(parse de HTML e de sitemap XML), `playwright` (navegador real para sites com JS/bloqueio).
Validação do contrato e do schema feita com Python puro (sem `jsonschema`), para manter as
dependências restritas a ferramentas de coleta (Princípio VI).
**Storage**: Arquivo `data/receitas.json` (sobrescrito de forma atômica). Sem banco.
**Testing**: `assert` nativo em um script Python para os helpers puros (validação de
registro, dedup, normalização, filtro de URL). Adaptadores dependentes de rede são
validados manualmente via quickstart (a rede é não-determinística).
**Target Platform**: Execução local por linha de comando (`python orquestrador.py`),
offline/sob demanda.
**Project Type**: Ferramenta CLI de scraping em Python — componente independente do frontend.
**Performance Goals**: ~5 sites × teto ~50 receitas = ~250 URLs por rodada; coleta educada
(User-Agent identificado, ritmo moderado). Playwright só quando necessário.
**Constraints**: nunca armazenar conteúdo de receita (III); única saída é `data/receitas.json`
(IV); saída conforme `receitas.schema.json` (V); gravação atômica; teto configurável por site.
**Scale/Scope**: pequeno — 5 adaptadores, centenas de URLs. Cresce por adição de adaptadores.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Avaliação contra os 8 princípios da constituição **v2.0.0**:

| Princípio | Veredito | Observação |
|-----------|----------|------------|
| I. Minimalismo Radical (UX) | ✅ N/A | O scraper não tem UI; não altera a tela. |
| II. Zero Fricção | ✅ N/A | Ferramenta de manutenção, não o fluxo do usuário final. |
| III. Redirecionar, Nunca Hospedar | ✅ PASS | Coleta só `{chef, site, titulo, url}` — o `titulo` é o nome da receita (rótulo), nunca o conteúdo (ingredientes/preparo/mídia). |
| IV. Separação Scraper ↔ Frontend | ✅ PASS | Única saída é `data/receitas.json`; nenhum arquivo do frontend é tocado. |
| V. Contrato Único dos Adaptadores | ✅ PASS | Todo adaptador retorna o mesmo registro; orquestrador valida contra o schema da Fase 1. |
| VI. Fundamentos sem Frameworks | ✅ PASS | A constituição autoriza explicitamente Python + BeautifulSoup + Playwright + parser de sitemap no scraper. Deps restritas a coleta; validação em Python puro. |
| VII. Aprendizado em Primeiro Lugar | ✅ PASS | Ordem sitemap→BS4→Playwright por site é justamente o exercício de aprendizado. |
| VIII. Escala por Adição | ✅ PASS | Novo site = novo `scrapers/<site>.py` + registro no orquestrador; nada mais muda. |

**Resultado: PASS, sem violações.** Complexity Tracking vazio.

## Project Structure

### Documentation (this feature)

```text
specs/002-scraper-receitas/
├── plan.md              # Este arquivo
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   └── adapter-contract.md   # Interface que todo adaptador implementa (aponta p/ o schema da Fase 1)
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks (não criado aqui)
```

### Source Code (repository root)

```text
cookAlaRoulette/
├── orquestrador.py          # Chama adaptadores, consolida, dedup, verifica URLs, grava JSON, relatório
├── requirements.txt         # beautifulsoup4, lxml, requests, playwright
├── scrapers/
│   ├── __init__.py
│   ├── base.py              # Contrato + helpers: GET educado, parse de sitemap, validação de registro, técnica-em-ordem
│   ├── panelinha.py         # Rita Lobo — BS4/sitemap (URLs /receita/)
│   ├── jamieoliver.py       # Jamie Oliver — sitemap/BS4 (URLs /recipes/<cat>/<slug>/)
│   ├── recipetineats.py     # Nagi — sitemap (catálogo completo; aprendizado do briefing)
│   ├── seriouseats.py       # Kenji — sitemap/BS4
│   └── maangchi.py          # Maangchi — caso bloqueado (403) → fallback Playwright
├── tests/
│   ├── sorteio.test.js      # (Fase 1 — intocado)
│   └── test_orquestrador.py # asserts dos helpers puros (validação, dedup, normalização, filtro de URL)
├── data/
│   └── receitas.json        # SAÍDA — sobrescrita pelo orquestrador; lida pelo frontend (NÃO editar à mão após a Fase 2)
└── (frontend da Fase 1: index.html, style.css, app.js, sorteio.js, assets/ — INTOCADOS)
```

**Structure Decision**: Materializa o `scrapers/` reservado na Fase 1. Cada adaptador é
isolado e expõe a mesma função de coleta; `base.py` concentra o que é comum (HTTP educado,
sitemap, validação) para os adaptadores não repetirem código nem vazarem formato. O
`orquestrador.py` é o único que escreve `data/receitas.json`. O schema do contrato é
**reusado** de `specs/001-fundacao-sorteio/contracts/receitas.schema.json` (fonte única).

## Complexity Tracking

> Constitution Check passou sem violações — nada a justificar.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (nenhuma) | — | — |
