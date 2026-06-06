# Data Model — Fase 4 — Refinamento

**Date**: 2026-06-05 · **Feature**: 004-refinamento

A Fase 4 **não altera o modelo de dados do produto** — `data/receitas.json` e o contrato
`{chef, site, titulo, url}` permanecem intocados (Princípio IV/V). As "entidades" desta fase são
metadados e estados de UI, não dados de runtime.

## Metadados sociais (no `<head>` do index.html)

| Campo | Valor |
|-------|-------|
| `lang` | `pt-BR` (já presente) |
| `<title>` / `meta description` | "Cook à la Roulette" / tagline (já presentes) |
| `og:title` | Cook à la Roulette |
| `og:description` | O universo decide o que você vai cozinhar hoje. |
| `og:image` | `assets/og-image.png` (1200×630) — URL absoluta na publicação |
| `og:url` | `https://felipekanarek.github.io/cookalaroulette/` |
| `og:type` | `website` |
| `twitter:card` | `summary_large_image` |

> A imagem é um asset referenciado no `<head>`, **não** um elemento visível da página (Princípio I).

## Estados da animação de clique (roleta de fontes)

| Estado | Comportamento |
|--------|---------------|
| ocioso | texto-marca na fonte sorteada da visita; botão habilitado |
| girando | ~0,8s alternando `--fonte` entre o subconjunto pré-carregado; botão desabilitado (FR-013) |
| reduced-motion | sem giro — vai direto ao redirecionamento |
| pós-clique | assenta numa fonte final e redireciona |

## Metadados do repositório (GitHub, via `gh`)

| Campo | Valor |
|-------|-------|
| LICENSE | MIT (arquivo na raiz) |
| description | curta, descrevendo o sorteador |
| homepage | `https://felipekanarek.github.io/cookalaroulette/` |
| topics | recipes, random, vanilla-js, web-scraping, spec-kit |

Nada disso é dado de runtime nem entra no `receitas.json`.
