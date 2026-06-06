# Research — Fase 4 — Refinamento

**Date**: 2026-06-05 · **Feature**: 004-refinamento

Decisões da Fase 0. Tudo em HTML/CSS/JS puro; Playwright só em build-time (gerar a OG image).

---

## 1. Contraste / cor da marca (WCAG AA)

**Decision**: **Manter o laranja `#e85d29`** no texto-marca. Medido: **3.26:1** sobre o
off-white `#faf7f2` → atende **WCAG 2.1 AA para texto grande** (≥3:1), que é exatamente o caso
(o texto-marca é enorme). O texto de status (`#555` sobre off-white) dá **6.98:1** → atende
AA-normal (≥4.5) com folga.

**Rationale**: respeita a cor escolhida pelo usuário e está conforme para o tamanho usado.
Mudar a cor seria desnecessário (e contra a identidade definida).

**Alternatives considered**: escurecer para `#c8410d` (4.66:1, passaria até AA-normal) — rejeitado,
pois o texto é grande e o `#e85d29` já é compliant; manteríamos a identidade.

---

## 2. Roleta de fontes no clique (FR-009)

**Decision**: pré-carregar um **subconjunto curado de fontes** (≈8–10 do pool, todas legíveis em
tamanho grande) injetando os `<link>` do Google Fonts no load. No clique: alternar a variável CSS
`--fonte` entre essas fontes a cada ~70–80ms por ~800ms (efeito de giro), então assentar numa
fonte final e redirecionar. Com `prefers-reduced-motion`: **sem giro** — vai direto (caminho atual).

**Rationale**: reusa o mecanismo de fonte aleatória; o preload do subconjunto evita o flicker de
fallback durante o giro. ~0,8s mantém o FR-005/Zero Fricção (não-interativo).

**Alternatives considered**: girar entre fontes não pré-carregadas (flicker de fallback) — rejeitado;
manter o fade (não é "design final") — rejeitado por decisão de escopo.

---

## 3. Imagem de prévia social (OG) 1200×630

**Decision**: `scripts/gerar_og.py` renderiza um HTML on-brand (fundo off-white, COOK À LA ROULETTE
em laranja, fonte display) para **`assets/og-image.png` (1200×630)** via screenshot do Playwright
(Chromium já instalado). É **build-time**: roda quando se quer (re)gerar a imagem; não faz parte do
site nem do runtime.

**Rationale**: PNG é o formato mais compatível com validadores de OG/Twitter (SVG nem sempre
renderiza). Reusa o Chromium que já temos, sem novas dependências de imagem (sem PIL etc.).

**Alternatives considered**: SVG como OG image (compatibilidade ruim) — rejeitado; ferramenta
externa/online — desnecessário.

---

## 4. Metadados sociais e SEO (FR-004)

**Decision**: no `<head>` do `index.html`, adicionar Open Graph (`og:title`, `og:description`,
`og:image` [1200×630], `og:url`, `og:type=website`) e Twitter Card (`summary_large_image`). `lang`
e `<title>`/`description` já existem. As tags são estáticas (não dependem de JS → o preview funciona
para crawlers).

**Rationale**: cobre os principais validadores; estático garante preview sem executar o sorteio.

---

## 5. Responsividade 320–1920px (FR-003)

**Decision**: ajustar o `clamp()` do texto-marca para garantir que a palavra mais larga
("ROULETTE") **não gere rolagem horizontal a 320px** em nenhuma fonte do pool — reduzir o fator
`vw` se necessário e manter `overflow-x: hidden` como rede. Verificar empiricamente em ~320px e em
desktop largo. Se alguma fonte do pool ainda estourar, **removê-la do pool** (a curadoria de
legibilidade da #2 já passa por isso).

**Rationale**: CSS responsivo simples + curadoria do pool resolve sem JS de "fit-to-width"
(mantém o frontend enxuto).

**Alternatives considered**: JS que encolhe a fonte até caber — mais robusto porém mais complexo;
adiável se o clamp + curadoria bastarem.

---

## 6. Acessibilidade — fechar o WCAG AA (FR-001)

**Decision**: auditar e fechar lacunas sobre o que já existe (piso da Fase 1):
- `<button>` em tela cheia já é focável e operável por teclado; garantir `:focus-visible` evidente
  (já há) e `aria-label` descritivo (já há).
- Região de status com `role="status" aria-live="polite"` (já há) — confirmar anúncio de
  carregando/erro.
- `prefers-reduced-motion`: desativar o giro (e qualquer transição incômoda).
- `lang="pt-BR"` e `<title>` (já há). Conferir contraste (item #1).
- Validar com auditoria automatizada (axe/Lighthouse) e operação 100% por teclado.

**Rationale**: a base já está boa (FR-015 da Fase 1); a fase fecha a auditoria completa e formaliza.

---

## 7. Metadados do repositório (FR-006)

**Decision**: criar `LICENSE` (MIT, 2026, Felipe Kanarek) na raiz; e via `gh repo edit` definir
descrição, **homepage** = `https://felipekanarek.github.io/cookalaroulette/` e topics (ex.: `recipes`,
`random`, `vanilla-js`, `web-scraping`, `spec-kit`). Requer a conta dona ativa no `gh` (já está).

**Rationale**: torna o repo público apresentável; `gh` aplica sem precisar da UI.
