# Implementation Plan: Fase 1 — Fundação (sorteio e redirecionamento)

**Branch**: `001-fundacao-sorteio` | **Date**: 2026-06-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-fundacao-sorteio/spec.md`

## Summary

Página única estática que sorteia uma receita curada em duas etapas (Chef → receita) e
redireciona a pessoa para a URL original no site do Chef. Tudo em HTML + CSS + JavaScript
puro (sem frameworks, sem build), lendo uma curadoria manual de `data/receitas.json`. A
lógica de sorteio é uma função pura e testável (garante distribuição uniforme por Chef);
a UI cuida do clique, da animação de roleta não-interativa (~0,8s), do redirecionamento em
nova aba e dos estados de vazio/erro. A estrutura reserva `scrapers/` para a Fase 2 sem
construí-la agora.

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript ES2020+ (vanilla). Python 3.11 reservado para
os scrapers da Fase 2 (não usado nesta fase, exceto como servidor estático local).
**Primary Dependencies**: Nenhuma. Sem frameworks, sem bundler, sem gerenciador de pacotes.
(Fase 2 introduzirá BeautifulSoup/Playwright — fora desta fase.)
**Storage**: Arquivo estático `data/receitas.json` (sem banco de dados).
**Testing**: Verificação manual no navegador (fluxo, responsividade, acessibilidade) +
um script Node com `assert` nativo para a distribuição do sorteio (sem framework de teste).
**Target Platform**: Navegadores modernos em mobile e desktop; servido como arquivos
estáticos.
**Project Type**: Web app estático de página única (frontend-only nesta fase).
**Performance Goals**: Página interativa imediatamente após carregar; animação de roleta
~0,8s; sorteio O(n) trivial sobre dezenas de Chefs / centenas de receitas.
**Constraints**: Sem frameworks, sem etapa de build, sem banco; responsivo; piso mínimo de
acessibilidade (teclado, foco, alt, contraste). `fetch` de JSON local exige servir os
arquivos via HTTP (não abrir por `file://`).
**Scale/Scope**: Curadoria inicial pequena (≥3 Chefs, ≥3 receitas cada na Fase 1; dezenas de
Chefs e centenas de receitas no horizonte). Uma única tela.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Avaliação contra os 8 princípios da constituição v1.0.0:

| Princípio | Veredito | Observação |
|-----------|----------|------------|
| I. Minimalismo Radical | ✅ PASS | Tela = 1 imagem + 1 botão; sem tagline, filtros, listas ou config. |
| II. Zero Fricção | ✅ PASS | Clique → animação **não-interativa** → redirect; sem cadastro. A animação não é etapa de decisão (FR-005). |
| III. Redirecionar, Nunca Hospedar | ✅ PASS | Armazena só `{chef, site, titulo, url}` e abre a URL original; nada de conteúdo. |
| IV. Separação Scraper ↔ Frontend | ✅ PASS | Frontend só **lê** `data/receitas.json`; `scrapers/` reservado e vazio nesta fase. |
| V. Contrato Único dos Adaptadores | ✅ PASS | `receitas.json` é um array de registros `{chef, site, titulo, url}` (ver contracts/). |
| VI. Fundamentos sem Frameworks | ✅ PASS | HTML/CSS/JS puro, JSON, sem build. Servidor estático local não é build (apenas serve arquivos). |
| VII. Aprendizado em Primeiro Lugar | ✅ PASS | `fetch`+HTTP, função de sorteio pura e testável, padrão de módulo browser/Node — todos didáticos. |
| VIII. Escala por Adição | ✅ PASS | Adicionar Chef = acrescentar registros ao JSON; sem mudança de arquitetura. |

**Resultado: PASS, sem violações.** Complexity Tracking vazio.

## Project Structure

### Documentation (this feature)

```text
specs/001-fundacao-sorteio/
├── plan.md              # Este arquivo (/speckit-plan)
├── research.md          # Fase 0 (/speckit-plan)
├── data-model.md        # Fase 1 (/speckit-plan)
├── quickstart.md        # Fase 1 (/speckit-plan)
├── contracts/
│   └── receitas.schema.json   # Schema do contrato de dados
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
cookAlaRoulette/
├── index.html              # Página única: imagem + botão "O que vou cozinhar?"
├── style.css               # Mood claro e arejado, responsivo, foco visível
├── app.js                  # UI: carrega dados, clique, animação, redirect, estados de erro
├── sorteio.js              # Lógica PURA do sorteio em duas etapas (browser + Node)
├── assets/
│   └── (imagem central)    # Uma imagem de apresentação
├── data/
│   └── receitas.json       # Curadoria manual: array de {chef, site, titulo, url}
├── tests/
│   └── sorteio.test.js     # Node + assert: distribuição ±10% e receita do Chef sorteado
├── scrapers/               # RESERVADO para a Fase 2 (não implementado agora)
│   └── README.md           # Documenta o contrato que os adaptadores deverão cumprir
├── BRIEFING.md
└── CLAUDE.md
```

> `orquestrador.py` e os adaptadores `scrapers/*.py` são **Fase 2** — não criados nesta
> fase. `scrapers/README.md` apenas registra o contrato esperado, cumprindo FR-011
> ("reservar espaço ... sem que estes sejam construídos nesta fase").

**Structure Decision**: Frontend na raiz (arquivos servidos diretamente) com os dados
isolados em `data/` e o futuro scraper isolado em `scrapers/` — refletindo a Separação
Estrita do Princípio IV. A lógica de sorteio fica em `sorteio.js` separada de `app.js`
para ser importável tanto pelo navegador quanto pelo teste Node, sem build.

## Complexity Tracking

> Constitution Check passou sem violações — nada a justificar.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (nenhuma) | — | — |
