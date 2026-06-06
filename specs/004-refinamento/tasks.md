---
description: "Task list — Fase 4 — Refinamento (acessibilidade, responsividade, lançamento)"
---

# Tasks: Fase 4 — Refinamento

**Input**: Design documents from `specs/004-refinamento/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/social-meta.md, quickstart.md

**Tests**: Esta fase NÃO tem testes de código — a validação é por **auditoria de acessibilidade**
(Lighthouse/axe), checagem de responsividade por redimensionamento, e validador de OG. (Conforme
spec; testes automatizados não foram solicitados.)

**Organization**: Por user story (P1 acessibilidade, P2 responsividade, P3 social/repo) + a roleta
de fontes (FR-009). Frontend-only + metadados do repo; scraper/dados intocados.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Confirmar ambiente (Playwright + Chromium já instalados, usados só p/ gerar a OG image; site segue sem dependências). Branch `004-refinamento` ativa.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: A curadoria do conjunto de fontes serve à legibilidade (a11y), à não-quebra de layout (responsivo) e à roleta de fontes.

- [X] T002 Curar o pool `FONTES` em `app.js`: manter só fontes legíveis em tamanho grande e que não estourem a largura; remover candidatas problemáticas (muito finas/estreitas/largas). Documentar o critério em comentário.

**Checkpoint**: pool de fontes confiável — base para US1, US2 e a roleta.

---

## Phase 3: User Story 1 - Acessibilidade WCAG AA (Priority: P1) 🎯

**Goal**: O site é 100% operável por teclado, com foco visível, contraste AA, ARIA correto e respeito a `prefers-reduced-motion`.

**Independent Test**: Navegar só por teclado (Tab→foco visível→Enter/Espaço aciona); auditoria axe/Lighthouse sem violações; `prefers-reduced-motion` ativo → sem animação incômoda.

### Implementation for User Story 1

- [X] T003 [US1] Em `style.css`: garantir `:focus-visible` evidente no gatilho; confirmar contraste — manter texto-marca `#e85d29` (3.26:1, AA-large ✓) e status `#555` (AA ✓); revisar `@media (prefers-reduced-motion: reduce)`.
- [X] T004 [US1] Em `index.html`: confirmar/reforçar `lang="pt-BR"`, `<title>`, `aria-label` do gatilho e a região `role="status" aria-live="polite"` (anúncio de carregando/erro a leitores de tela).
- [X] T005 [US1] Rodar auditoria de acessibilidade (Lighthouse/axe) + teste só-teclado; corrigir lacunas até **0 violações** WCAG AA (SC-001).

**Checkpoint**: acessibilidade fechada (a auditoria adiada da Fase 1).

---

## Phase 4: User Story 2 - Responsividade 320–1920px (Priority: P2)

**Goal**: Texto-marca centrado, sem corte nem rolagem horizontal, de celulares estreitos a desktops largos.

**Independent Test**: Redimensionar de 320px a 1920px (várias fontes sorteadas) e confirmar 0 rolagem horizontal e 0 corte.

### Implementation for User Story 2

- [X] T006 [US2] Em `style.css`: ajustar o `clamp()` do texto-marca para "ROULETTE" caber a 320px em qualquer fonte do pool; manter `overflow-x: hidden` como rede.
- [X] T007 [US2] Verificar em 320/375/768/1280/1920px; se alguma fonte do pool ainda estourar, removê-la (sincronizar com `app.js`/T002) e reconferir (SC-002).

**Checkpoint**: layout sólido em qualquer tela.

---

## Phase 5: User Story 3 - Compartilhável + repositório apresentável (Priority: P3)

**Goal**: Preview social bonito ao compartilhar o link; repo com licença, descrição e homepage.

**Independent Test**: Validar a URL num checker de OG (título+descrição+imagem); abrir o repo e ver LICENSE + descrição + homepage.

### Implementation for User Story 3

- [X] T008 [P] [US3] Criar `scripts/gerar_og.py` (Playwright, build-time): renderiza HTML on-brand → `assets/og-image.png` (1200×630, COOK À LA ROULETTE laranja sobre off-white). Rodar para gerar o asset.
- [X] T009 [US3] Em `index.html` `<head>`: adicionar tags Open Graph + Twitter Card (título, descrição, `og:image` ABSOLUTA, `og:url`, `summary_large_image`) conforme `contracts/social-meta.md`.
- [X] T010 [P] [US3] Criar `LICENSE` (MIT, 2026, Felipe Kanarek) na raiz.
- [X] T011 [P] [US3] `gh repo edit felipekanarek/cookalaroulette` — definir description, homepage (URL do Pages) e topics (recipes, random, vanilla-js, web-scraping, spec-kit). (Conta dona ativa no gh.)

**Checkpoint**: link compartilhável e repo apresentável (SC-005, SC-006).

---

## Phase 6: Roleta de fontes (FR-009)

**Goal**: Substituir o fade do clique pela tipografia "girando" entre fontes por ~0,8s.

**Independent Test**: Clicar e ver a fonte trocar rápido ~0,8s antes do redirect; com `prefers-reduced-motion`, vai direto (sem giro).

- [X] T012 [US1] Em `app.js`: pré-carregar um subconjunto de fontes do pool e, no clique, alternar `--fonte` entre elas a cada ~70–80ms por ~0,8s, assentar e redirecionar; **pular o giro** quando `prefers-reduced-motion` (mantém FR-013 — botão desabilitado durante o giro). Ajustar `style.css` se necessário (remover/garantir a classe de fade antiga).

**Checkpoint**: roleta de fontes no ar, acessível.

---

## Phase 7: Polish & Lançamento

- [X] T013 Validação final pelo `quickstart.md`: auditoria AA sem violações (SC-001), 0 rolagem horizontal 320–1920 (SC-002), reduced-motion sem giro (SC-003), contraste das fontes (SC-004), preview OG (SC-005), metadados do repo (SC-006).
- [X] T014 [P] Atualizar README/constituição se algo mudou de comportamento (ex.: roleta de fontes); marcar a Fase 4 como concluída onde fizer sentido.
- [X] T015 **Merge** da branch `004-refinamento` em `main` e `git push` — o GitHub Pages republica automaticamente o site refinado.

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002, pool de fontes)** → user stories.
- **US1 (P1)**: T003 (style.css) → T004 (index.html) → T005 (auditoria). MVP do refino.
- **US2 (P2)**: T006 → T007 (style.css; depende do pool T002; sequencial com T003 por editar style.css).
- **US3 (P3)**: T008 (og script, [P]) → T009 (index.html — sequencial com T004 por editar index.html); T010 (LICENSE, [P]); T011 (gh, [P]).
- **Roleta de fontes (T012)**: edita `app.js` (e `style.css`) — sequenciar com T002/T003.
- **Polish (T013–T015)**: depois de tudo; T015 (merge→Pages) é o último.

### Conflitos de arquivo (sequenciar, não paralelizar)
- `style.css`: T003, T006, T012 → mesma ordem das fases.
- `index.html`: T004, T009 → T004 antes de T009.
- `app.js`: T002, T012 → T002 antes de T012.

### Paralelizáveis [P]
- T008 (scripts/gerar_og.py), T010 (LICENSE), T011 (gh) — arquivos/alvos distintos.

---

## Implementation Strategy

1. Setup + Foundational (pool de fontes).
2. **US1 (acessibilidade)** — o coração do refino; valida com auditoria.
3. **US2 (responsividade)** — verificar/ajustar em telas reais.
4. **Roleta de fontes** — o toque de "design final".
5. **US3 (social/repo)** — OG image, meta, LICENSE, metadados do repo.
6. Polish → **merge em main → Pages republica** o site refinado.

Cada bloco é um incremento entregável; dá pra parar e validar a qualquer momento.

## Notes

- Sem testes de código (validação por auditoria/checagem manual, conforme spec).
- Nada toca scraper, `orquestrador.py` ou `receitas.json` (Princípio IV).
- Nenhum elemento visível novo na tela (Princípio I) — só `<head>`, CSS, JS de animação, assets e metadados.
- Projeto agora é git: trabalho na branch `004-refinamento`; lançamento = merge em `main`.
