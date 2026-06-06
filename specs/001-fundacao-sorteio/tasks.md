---
description: "Task list — Fase 1 — Fundação (sorteio e redirecionamento)"
---

# Tasks: Fase 1 — Fundação (sorteio e redirecionamento)

**Input**: Design documents from `specs/001-fundacao-sorteio/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/receitas.schema.json, quickstart.md

**Tests**: Inclui um teste automatizado (Node + `assert`) para a distribuição do sorteio,
explicitamente solicitado (SC-003). O restante da validação é manual no navegador
(quickstart.md). Sem framework de teste, sem build, sem git.

**Organization**: Tarefas agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependências pendentes)
- **[Story]**: a qual user story a tarefa pertence (US1, US2, US3)
- Caminhos relativos à raiz do projeto `/Users/infoprice/cookAlaRoulette/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Criar a estrutura de pastas e os placeholders da Fase 2.

- [X] T001 Criar a estrutura de diretórios na raiz: `assets/`, `data/`, `tests/`, `scrapers/`
- [X] T002 [P] Criar `scrapers/README.md` documentando o contrato `{chef, site, titulo, url}` que os adaptadores da Fase 2 deverão cumprir (FR-011) — sem código Python
- [X] T003 [P] Adicionar uma imagem de apresentação em `assets/` (ex.: `assets/prato.jpg`) para a imagem central da página — usar imagem **própria ou royalty-free** (ex.: Unsplash/Pexels), coerente com o respeito à autoria (Princípio III), e registrar crédito/licença em `assets/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Núcleo compartilhado pelas user stories — dados, lógica pura de sorteio e o esqueleto da página.

**⚠️ CRITICAL**: Nenhuma user story começa antes desta fase terminar.

- [X] T004 Criar `data/receitas.json` com curadoria manual conforme `contracts/receitas.schema.json`: ≥3 Chefs de países diferentes, ≥3 receitas reais cada, no formato `{chef, site, titulo, url}`
- [X] T005 [P] Implementar a lógica PURA de sorteio em `sorteio.js`: validar registros (campos não-vazios, `url` http(s)), agrupar por Chef, sorteio em duas etapas (Chef uniforme → receita), retornar `null` se não houver Chef elegível; expor as funções com guard `if (typeof module !== 'undefined' && module.exports) module.exports = {...}` para uso no navegador e no Node
- [X] T006 Criar o esqueleto de `index.html` referenciando `style.css`, `sorteio.js` e `app.js`: `<img>` com `alt` descritivo, um `<button>` semântico rotulado "O que vou cozinhar?", e uma região de status `role="status" aria-live="polite"` para mensagens de vazio/erro

**Checkpoint**: dados, lógica de sorteio e estrutura HTML prontos — user stories podem começar.

---

## Phase 3: User Story 1 - Sortear uma receita e ir cozinhar (Priority: P1) 🎯 MVP

**Goal**: Clicar no botão → animação breve de roleta → redirecionamento para a URL original de uma receita real.

**Independent Test**: Servir o site (`python3 -m http.server 8000`), abrir, clicar em "O que vou cozinhar?" e verificar que o navegador chega a uma receita real no domínio de um Chef da lista; repetir cliques e ver receitas diferentes.

### Implementation for User Story 1

- [X] T007 [US1] Implementar o carregamento dos dados em `app.js`: `fetch('data/receitas.json')` (relativo a `index.html` na raiz), `JSON.parse`, montar o mapa Chef→receitas usando as funções de `sorteio.js`, e definir o estado OK (botão habilitado)
- [X] T008 [US1] Implementar os estados de **vazio** (FR-008) e de **falha de carregamento** (FR-014) em `app.js`: mensagens amigáveis **distintas** na região de status e botão desabilitado; envolver `fetch`+parse em `try/catch` e tratar HTTP ≠ 2xx e raiz não-array
- [X] T009 [US1] Implementar o handler de clique + a animação de roleta (~0,8s) em `app.js` e `style.css` (CSS `@keyframes` + toggle de classe; respeitar `prefers-reduced-motion` com transição mínima)
- [X] T010 [US1] Implementar o redirecionamento em `app.js` ao fim da animação: `window.open(url, '_blank', 'noopener')` com fallback para `window.location.assign(url)` se o popup for bloqueado
- [X] T011 [US1] Implementar FR-013 em `app.js`: desabilitar o botão durante a animação (ignorar cliques concorrentes) e reabilitar após o redirecionamento

**Checkpoint**: página clicável e funcional ponta a ponta — MVP entregável.

---

## Phase 4: User Story 2 - Descoberta equilibrada entre Chefs (Priority: P2)

**Goal**: Garantir que cada Chef tem chance igual de ser sorteado, independentemente do tamanho do catálogo.

**Independent Test**: `node tests/sorteio.test.js` — executa ≥1000 sorteios e verifica que cada Chef fica dentro de ±10% da frequência esperada (1/nº de Chefs) e que a receita sorteada pertence ao Chef sorteado.

### Tests for User Story 2

- [X] T012 [P] [US2] Escrever o teste de distribuição em `tests/sorteio.test.js` (Node + `assert` nativo): `require('../sorteio.js')`, montar uma curadoria com Chefs de tamanhos de catálogo diferentes, rodar ≥1000 sorteios, asserir (a) cada Chef dentro de ±10% de 1/N e (b) a receita sorteada pertence ao Chef sorteado

### Implementation for User Story 2

- [X] T013 [US2] Rodar `node tests/sorteio.test.js` e garantir que todas as asserções passam; ajustar `sorteio.js` se a distribuição estiver enviesada (o sorteio do Chef deve ser uniforme sobre Chefs, nunca sobre receitas)

**Checkpoint**: distribuição validada automaticamente.

---

## Phase 5: User Story 3 - Experiência sofisticada em qualquer tela (Priority: P3)

**Goal**: Tela elegante, clara e arejada, centrada e responsiva em mobile e desktop, com piso de acessibilidade.

**Independent Test**: Abrir o site em largura de celular e de desktop e verificar imagem e botão centrados, legíveis, sem rolagem horizontal; navegar até o botão por teclado com foco visível.

### Implementation for User Story 3

- [X] T014 [US3] Implementar o layout responsivo em `style.css`: imagem e botão centrados em telas estreitas e largas, sem rolagem horizontal, dimensionamento fluido
- [X] T015 [US3] Aplicar o mood "claro e arejado" em `style.css`: paleta clara, amplo espaço em branco, tipografia refinada — evitando aparência de "sorteador de bingo" (FR-012)
- [X] T016 [US3] Polir o piso de acessibilidade (FR-015) em `style.css`: `:focus-visible` evidente no botão e verificar contraste de texto AA no tema claro (alt da imagem e operação por teclado já vêm do HTML semântico do T006)

**Checkpoint**: todas as user stories independentemente funcionais.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e conformidade com a constituição.

- [X] T017 Rodar a validação do `quickstart.md`: checagens manuais de US1 e US3 + `node tests/sorteio.test.js`; testar os estados vazio (`[]`) e falha (JSON inválido)
- [X] T018 [P] Verificar conformidade com a constituição: tela mostra apenas imagem + botão, sem tagline (SC-005); nenhum conteúdo de receita é hospedado (Princípio III); `scrapers/` permanece sem código (Princípio IV / FR-011)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências — começa imediatamente
- **Foundational (Phase 2)**: depende do Setup — BLOQUEIA todas as user stories
- **User Stories (Phase 3–5)**: dependem da Foundational
  - US1 (P1): precisa de T004, T005, T006
  - US2 (P2): precisa de T004 e T005 (lógica pura) — **independente de US1**, pode rodar em paralelo
  - US3 (P3): precisa de T006 — pode refinar em paralelo a US1/US2
- **Polish (Phase 6)**: depende das user stories desejadas concluídas

### Within Each User Story

- US1: T007 (carregar dados) → T008 (estados) → T009 (clique+animação) → T010 (redirect) → T011 (FR-013)
- US2: T012 (escrever teste) → T013 (rodar e ajustar)
- US3: T014 → T015 → T016

### Parallel Opportunities

- Setup: T002 e T003 em paralelo
- Foundational: T005 [P] (sorteio.js) em paralelo a T006 (index.html) — arquivos diferentes
- US2 inteira pode correr em paralelo a US1 (toca só `tests/` e lê `sorteio.js`)
- US3 (estilos) pode correr em paralelo a US1 (lógica), pois mexem em arquivos/aspectos distintos

---

## Parallel Example: Foundational

```bash
# Após T004 (dados), rodar em paralelo:
Task: "T005 Implementar lógica pura de sorteio em sorteio.js"
Task: "T006 Criar esqueleto de index.html"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1: Setup
2. Phase 2: Foundational (CRÍTICO — bloqueia tudo)
3. Phase 3: US1 — sortear e redirecionar
4. **PARAR e VALIDAR**: testar US1 ponta a ponta no navegador
5. É o MVP demonstrável

### Incremental Delivery

1. Setup + Foundational → base pronta
2. US1 → testar → MVP (sorteio + redirect funcionando)
3. US2 → `node tests/sorteio.test.js` valida a distribuição equilibrada
4. US3 → polir responsividade, mood claro e arejado, acessibilidade
5. Polish → validação do quickstart + conformidade com a constituição

---

## Notes

- [P] = arquivos diferentes, sem dependências pendentes
- Sem build, sem frameworks: o "deploy" local é `python3 -m http.server` servindo a raiz
- `fetch` exige servir por HTTP — não abrir `index.html` por `file://`
- Projeto sem git: não há tarefas de branch/commit
- Parar em qualquer checkpoint para validar a story isoladamente
