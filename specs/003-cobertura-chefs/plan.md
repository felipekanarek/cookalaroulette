# Implementation Plan: Fase 3 — Integração e ampliação de cobertura

**Branch**: `003-cobertura-chefs` | **Date**: 2026-06-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/003-cobertura-chefs/spec.md`

## Summary

Escalar o scraper da Fase 2 para cobrir os 38 chefs / 25 países do briefing. Duas técnicas
reutilizáveis são generalizadas em `scrapers/base.py` — (a) busca de sitemap via navegador
real (corpo bruto, recursando índices — lição da Maangchi) e (b) crawl de páginas de
listagem (BeautifulSoup, com Playwright só quando a listagem é JS) — para que cada novo
adaptador apenas declare seu padrão de URL e a técnica. Os ~35 adaptadores restantes são
adicionados e registrados no orquestrador, que continua consolidando, deduplicando,
verificando URLs vivas e gravando `data/receitas.json` (nunca vazio). Frontend intocado
(Princípio IV). Re-indexação manual sob demanda.

## Technical Context

**Language/Version**: Python 3.9 (ambiente atual).
**Primary Dependencies**: já instaladas na Fase 2 — `requests`, `beautifulsoup4`, `lxml`,
`playwright` (+ Chromium). Sem novas dependências.
**Storage**: `data/receitas.json` (atômico). Sem banco.
**Testing**: `assert` nativo (Python) para os novos helpers puros (filtro de listagem,
extração de links); adaptadores dependentes de rede validados via execução + relatório.
**Target Platform**: CLI local (`python orquestrador.py`), offline/sob demanda.
**Project Type**: ferramenta CLI de scraping (independente do frontend).
**Performance Goals**: ~38 sites × teto ~50 = até ~1900 URLs por rodada; coleta educada
(rate limit, timeout por site). Playwright só quando necessário (bloqueio/JS). Tolerar
rodadas de vários minutos.
**Constraints**: nunca armazenar conteúdo (III); única saída `data/receitas.json` (IV);
contrato `{chef, site, titulo, url}` (V); gravação atômica; nunca sobrescrever com vazio;
falha isolada não derruba a rodada.
**Scale/Scope**: 38 adaptadores (3 já feitos, ~35 novos). Cresce por adição (VIII).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Contra a constituição **v2.0.0**:

| Princípio | Veredito | Observação |
|-----------|----------|------------|
| I. Minimalismo Radical (UX) | ✅ N/A | Sem UI; frontend não muda. |
| II. Zero Fricção | ✅ N/A | Ferramenta de manutenção. |
| III. Redirecionar, Nunca Hospedar | ✅ PASS | Só `{chef, site, titulo, url}`; `titulo` = nome (rótulo), nunca conteúdo. |
| IV. Separação Scraper ↔ Frontend | ✅ PASS | Única saída `data/receitas.json`; frontend intocado. |
| V. Contrato Único | ✅ PASS | Todos os adaptadores no mesmo formato; orquestrador valida. |
| VI. Fundamentos sem Frameworks | ✅ PASS | Stack autorizada (BS4/Playwright/sitemap); validação em Python puro. |
| VII. Aprendizado em Primeiro Lugar | ✅ PASS | Cada site bespoke ensina; escalonamento de técnica explícito. |
| VIII. Escala por Adição | ✅ PASS | Novo chef = novo `scrapers/<site>.py` + registro; nada mais muda. |

**Resultado: PASS, sem violações.** Complexity Tracking vazio.

## Project Structure

### Documentation (this feature)

```text
specs/003-cobertura-chefs/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/
│   └── chefs-catalog.md       # os 38 chefs: domínio, país, técnica planejada, status
└── checklists/requirements.md
```

### Source Code (repository root)

```text
cookAlaRoulette/
├── orquestrador.py            # ADAPTADORES estendido com os ~35 novos
├── scrapers/
│   ├── base.py                # + coletar_por_sitemap_browser()  + coletar_por_listagem()
│   ├── (3 da Fase 2: recipetineats, jamieoliver, maangchi, panelinha*, seriouseats*)
│   └── <novo_chef>.py × ~35   # um por chef restante
├── tests/
│   └── test_scrapers.py       # asserts dos novos helpers puros (extração de links/listagem)
└── data/receitas.json         # SAÍDA — ampliada; frontend intocado
```

\* `panelinha.py` (reescrito p/ listagem) e `seriouseats.py` (reescrito p/ fallback browser)
já existem da Fase 2 mas serão completados aqui.

**Structure Decision**: Mantém a arquitetura da Fase 2 (Princípio VIII): toda a inteligência
nova compartilhada vai para `base.py` (2 helpers), e cada chef é um arquivo pequeno que só
declara `CHEF/SITE/TECNICAS` + filtro de URL. A entrega é organizada em **lotes por
técnica** (ver tasks): sitemap → sitemap-via-browser (bloqueados) → listagem (sem sitemap).

## Complexity Tracking

> Constitution Check passou sem violações.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (nenhuma) | — | — |
