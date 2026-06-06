# Quickstart — Fase 4 — Refinamento

**Feature**: 004-refinamento · **Date**: 2026-06-05

Como validar os refinamentos. Site continua HTML/CSS/JS puro; nada novo a instalar (Playwright já
está, e é só para (re)gerar a imagem OG).

## Servir e testar localmente

```bash
cd /Users/infoprice/cookAlaRoulette
python3 -m http.server 8000     # abrir http://localhost:8000/
```

## Acessibilidade (FR-001 / SC-001, SC-003)

- **Só teclado**: Tab até o texto-marca → foco visível → Enter/Espaço aciona o sorteio.
- **Auditoria**: rodar Lighthouse/axe (DevTools → Lighthouse → Accessibility) → sem violações de
  contraste, nome/rótulo, idioma, foco.
- **Reduzir movimento**: ativar `prefers-reduced-motion` no SO/navegador → clicar → **sem giro**
  de fontes, redireciona direto.
- **Contraste**: texto-marca `#e85d29` sobre off-white = 3.26:1 (AA-large ✓); status `#555` = 6.98:1.

## Responsividade (FR-003 / SC-002)

- DevTools → modo responsivo → testar **320px, 375px, 768px, 1280px, 1920px**.
- Conferir: "COOK / A LA / ROULETTE" centrado, sem corte, **sem rolagem horizontal** em nenhuma
  largura, em várias fontes (recarregar para sortear fontes diferentes).

## Roleta de fontes (FR-009)

- Clicar e observar a tipografia "girar" (~0,8s) antes de abrir a receita.
- Com reduced-motion: deve ir direto, sem giro.

## (Re)gerar a imagem OG (FR-004/FR-005)

```bash
python3 scripts/gerar_og.py     # gera assets/og-image.png (1200×630) via Playwright
```

Validar o preview: colar a URL pública em https://www.opengraph.xyz/ (ou similar) → ver
título + descrição + imagem.

## Metadados do repositório (FR-006 / SC-006)

```bash
# conta dona ativa no gh (felipekanarek)
gh repo edit felipekanarek/cookalaroulette \
  --description "Sorteador de receitas que redireciona para o site original do Chef. O universo decide o que você vai cozinhar hoje." \
  --homepage "https://felipekanarek.github.io/cookalaroulette/" \
  --add-topic recipes --add-topic random --add-topic vanilla-js \
  --add-topic web-scraping --add-topic spec-kit
```

E conferir que existe o arquivo `LICENSE` (MIT) na raiz.

## Publicar

Como o deploy é GitHub Pages a partir de `main`, ao final faça merge da branch `004-refinamento`
em `main` e dê push — o Pages republica automaticamente.
