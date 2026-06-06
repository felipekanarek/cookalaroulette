# Implementation Plan: Fase 4 — Refinamento (acessibilidade, responsividade, lançamento)

**Branch**: `004-refinamento` | **Date**: 2026-06-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/004-refinamento/spec.md`

## Summary

Polir o app já publicado para um lançamento responsável: fechar a **acessibilidade WCAG 2.1
AA** (adiada da Fase 1), **verificar/ajustar a responsividade** do redesign tipográfico
(320px→desktop), adicionar **metadados sociais** (Open Graph/Twitter + imagem 1200×630) e
**metadados do repositório** (LICENSE MIT, descrição, homepage), e trocar o fade do clique
pela **"roleta de fontes"** (com fallback `prefers-reduced-motion`). Tudo em HTML/CSS/JS puro;
mexe só no frontend e em metadados — scraper/dados intocados (Princípio IV).

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript ES2020+ (vanilla) — mesmo do frontend atual.
**Primary Dependencies**: nenhuma nova **no site**. Google Fonts (já em uso) para a roleta de
fontes. Playwright (já instalado) usado **só em build-time** para gerar a imagem OG (renderizar
HTML→PNG) — não é dependência de runtime nem é embarcado no site.
**Storage**: nenhuma mudança em dados (`receitas.json` intocado). Novo asset estático
`assets/og-image.png`.
**Testing**: verificação manual + ferramenta de auditoria de acessibilidade (ex.: Lighthouse/
axe no navegador) para contraste/teclado/rotulagem; checagem de responsividade por
redimensionamento (320–1920px); validação do preview OG.
**Target Platform**: navegadores modernos (mobile + desktop); hospedado em GitHub Pages (já no ar).
**Project Type**: web app estático de página única (frontend-only) + metadados de repositório.
**Performance Goals**: a roleta de fontes não deve travar (cycle suave ~80ms); preload de um
subconjunto de fontes para evitar flicker; página continua leve.
**Constraints**: sem frameworks/sem build no site (Princípio VI); nenhum elemento visível novo
na tela (Princípio I); reduced-motion respeitado (Princípio II); só frontend + repo (Princípio IV).
**Scale/Scope**: alguns arquivos do frontend + 1 asset + LICENSE + config do repo. Pequeno.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Contra a constituição **v2.0.0**:

| Princípio | Veredito | Observação |
|-----------|----------|------------|
| I. Minimalismo Radical (UX) | ✅ PASS | Nada visível novo na tela; OG/meta no `<head>`, LICENSE e og-image não são UI da página. |
| II. Zero Fricção | ✅ PASS | Roleta de fontes é não-interativa e respeita `prefers-reduced-motion`. |
| III. Redirecionar, Nunca Hospedar | ✅ N/A | Não muda coleta/conteúdo. |
| IV. Separação Scraper ↔ Frontend | ✅ PASS | Mexe só no frontend e em metadados do repo; scraper/dados intocados. |
| V. Contrato Único | ✅ N/A | `receitas.json` inalterado. |
| VI. Fundamentos sem Frameworks | ✅ PASS | Site segue HTML/CSS/JS puro, sem build. Playwright só gera a OG image em build-time (não embarcado). |
| VII. Aprendizado em Primeiro Lugar | ✅ PASS | A11y, OG, fontes — fundamentos da web. |
| VIII. Escala por Adição | ✅ N/A | — |

**Resultado: PASS, sem violações.** Complexity Tracking vazio.

## Project Structure

### Documentation (this feature)

```text
specs/004-refinamento/
├── plan.md · research.md · data-model.md · quickstart.md
├── contracts/
│   └── social-meta.md    # tags OG/Twitter exigidas (contrato com crawlers sociais)
└── checklists/requirements.md
```

### Source Code (repository root)

```text
cookAlaRoulette/
├── index.html        # + meta OG/Twitter no <head> (título/descrição/imagem/idioma)
├── style.css         # responsivo 320–1920, :focus-visible, contraste AA, prefers-reduced-motion
├── app.js            # roleta de fontes (preload de subconjunto + cycle ~0,8s) substituindo o fade
├── assets/
│   ├── favicon.svg            # (existente)
│   └── og-image.png           # NOVO — prévia social 1200×630 (gerada via Playwright)
├── scripts/
│   └── gerar_og.py            # NOVO — build-time: renderiza HTML→PNG da OG image (não embarcado)
├── LICENSE                    # NOVO — MIT
└── (scraper, data, specs — INTOCADOS)
```

**Structure Decision**: Mudanças cirúrgicas nos 3 arquivos do frontend + 1 asset + 1 helper de
build + LICENSE. Os metadados do repositório (descrição/homepage/topics) são aplicados via `gh`
(não são arquivos). Nada no scraper, nos dados ou nas specs anteriores.

## Complexity Tracking

> Constitution Check passou sem violações.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (nenhuma) | — | — |
