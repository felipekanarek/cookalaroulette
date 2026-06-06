# Contrato — Metadados sociais (Open Graph / Twitter)

**Feature**: 004-refinamento · **Date**: 2026-06-05

A única "interface externa" nova desta fase é o conjunto de metadados que os **crawlers de
preview** (WhatsApp, Slack, X/Twitter, Facebook, etc.) leem do `<head>` do `index.html`. Devem
ser **estáticos** (sem depender de JS) para funcionar com crawlers que não executam scripts.

## Tags obrigatórias no `<head>`

```html
<meta property="og:type"        content="website">
<meta property="og:title"       content="Cook à la Roulette">
<meta property="og:description" content="O universo decide o que você vai cozinhar hoje.">
<meta property="og:url"         content="https://felipekanarek.github.io/cookalaroulette/">
<meta property="og:image"       content="https://felipekanarek.github.io/cookalaroulette/assets/og-image.png">
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="Cook à la Roulette">
<meta name="twitter:description" content="O universo decide o que você vai cozinhar hoje.">
<meta name="twitter:image"       content="https://felipekanarek.github.io/cookalaroulette/assets/og-image.png">
```

## Requisitos da imagem

- `assets/og-image.png` — **1200×630** (proporção 1.91:1, padrão OG).
- On-brand: fundo off-white `#faf7f2`, texto **COOK À LA ROULETTE** em laranja `#e85d29`.
- Gerada por `scripts/gerar_og.py` (build-time, via Playwright). Não é UI da página.

## Aceite

- Um validador de OG/Twitter (ou um app de mensagens) mostra **título + descrição + imagem**.
- As tags estão no HTML servido (não injetadas por JS).
- A `og:image` aponta para URL **absoluta** (crawlers não resolvem relativas de forma confiável).
