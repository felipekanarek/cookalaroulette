# Research — Fase 1 — Fundação (sorteio e redirecionamento)

**Date**: 2026-06-05 · **Feature**: 001-fundacao-sorteio

Decisões técnicas tomadas na Fase 0. Todas compatíveis com a constituição v1.0.0
(HTML/CSS/JS puro, JSON, sem frameworks, sem build).

---

## 1. Como o frontend lê `receitas.json`

**Decision**: Carregar via `fetch('data/receitas.json')` (caminho relativo a partir de
`index.html` na raiz) e servir os arquivos por HTTP com um servidor estático local
(`python3 -m http.server 8000` a partir da raiz do projeto, abrindo `http://localhost:8000/`).

**Rationale**: `fetch` é a forma idiomática e didática de ler um arquivo de dados no
navegador, e prepara o terreno para o deploy da Fase 4 (que servirá os arquivos por HTTP de
qualquer forma). Abrir `index.html` por `file://` faz o navegador bloquear o `fetch` por
política de mesma origem (CORS) — esse atrito é, na verdade, um bom momento de aprendizado
sobre HTTP e origens (Princípio VII).

**Alternatives considered**:
- **`receitas.js` definindo `window.RECEITAS = [...]`** e incluído por `<script>`: abriria
  por `file://` sem servidor, mas desviaria do `receitas.json` nomeado na constituição e
  ensinaria menos sobre `fetch`/HTTP. Rejeitado.
- **Embutir os dados inline no `index.html`**: viola a separação dados ↔ apresentação
  (Princípio IV). Rejeitado.

---

## 2. Sorteio em duas etapas com Chef uniforme

**Decision**: Função pura `sortear(receitas)`:
1. Agrupar os registros por Chef em memória (no carregamento).
2. Filtrar Chefs sem receitas válidas e receitas sem URL válida (FR-007).
3. Sortear **um Chef** com `Math.random()` uniforme sobre a lista de Chefs (não sobre as
   receitas).
4. Sortear **uma receita** uniformemente dentro do Chef escolhido.
5. Retornar a receita (ou `null` se não houver Chefs/receitas válidos).

**Rationale**: Sortear o Chef primeiro, independente do tamanho do catálogo, dá a cada Chef
a mesma probabilidade (`1/nº de Chefs`) — exatamente o que SC-003/US2 exigem (±10% em ≥1000
sorteios). Função pura e sem efeitos colaterais → testável isoladamente em Node.

**Alternatives considered**:
- **Sorteio uniforme sobre todas as receitas**: simples, mas favorece Chefs com catálogos
  maiores — viola a "descoberta equilibrada". Rejeitado.

---

## 3. Compartilhar a lógica entre navegador e teste (sem build)

**Decision**: `sorteio.js` define as funções puras e expõe-as nos dois ambientes com um
guard: `if (typeof module !== 'undefined' && module.exports) module.exports = { ... }`. No
navegador é carregado por `<script src="sorteio.js">` (funções no escopo global); no Node é
carregado por `require('../sorteio.js')`.

**Rationale**: Permite um teste automatizado da distribuição sem introduzir bundler nem
framework de teste — apenas o `assert` nativo do Node. Padrão UMD-simplificado é didático.

**Alternatives considered**:
- **ES Modules (`import`/`export`)**: exigiria `type="module"` e ajustes de servir/CORS, e
  `node --experimental` ou `.mjs`; mais fricção para um projeto de aprendizado. Adiável.
- **Sem teste automatizado (só console)**: menos rigor para validar SC-003. Rejeitado.

---

## 4. Animação de roleta não-interativa (~0,8s)

**Decision**: Animação por CSS (`@keyframes` + classe alternada via JS) disparada no clique;
ao final (via `setTimeout`/`animationend`, ~800ms) ocorre o redirecionamento. Durante a
animação o botão recebe `disabled`/`aria-disabled` e ignora cliques (FR-013). Respeitar
`prefers-reduced-motion`: quem prefere menos movimento recebe uma transição mínima/instante.

**Rationale**: CSS keyframes são leves, fluidas e sem dependências. O `disabled` no botão é a
forma mais simples e previsível de ignorar cliques concorrentes. `prefers-reduced-motion`
sustenta o piso de acessibilidade (FR-015) sem custo.

**Alternatives considered**:
- **Animação por JS (requestAnimationFrame)**: mais controle, mais código; desnecessário
  para um efeito de 0,8s. Rejeitado.

---

## 5. Redirecionamento (nova aba com fallback)

**Decision**: `window.open(url, '_blank')` e, no sucesso, `nova.opener = null` para a
proteção de segurança; se o retorno for `null` (popup bloqueado), cair para
`window.location.assign(url)` na mesma aba.

**Rationale**: Atende a Assumption "nova aba preserva a roleta para sortear de novo", com
fallback robusto quando o popup é bloqueado, e desanexa o `opener` por segurança.

> ⚠️ **Não usar `'noopener'` na string de features do `window.open`**: com `'noopener'`, o
> `window.open` retorna `null` **mesmo quando a aba abre com sucesso** — isso fazia o
> fallback disparar e abrir o link nas DUAS abas ao mesmo tempo. A proteção é obtida com
> `nova.opener = null` em vez da feature.

**Alternatives considered**:
- **Sempre mesma aba (`location.assign`)**: perde o ciclo "sortear de novo" sem precisar
  voltar. Rejeitado como padrão (mantido só como fallback).

---

## 6. Estados de vazio e de falha de carregamento

**Decision**: Três estados distintos no carregamento:
- **OK**: há ≥1 receita válida → botão habilitado.
- **Vazio** (FR-008): carregou mas 0 receitas válidas → mensagem "sem receitas no momento",
  botão desabilitado.
- **Falha** (FR-014): `fetch` rejeitou, HTTP ≠ 2xx, ou `JSON.parse`/estrutura inválida →
  mensagem **distinta** "não foi possível carregar as receitas agora", botão desabilitado.

**Rationale**: Distinguir "vazio" de "erro" dá feedback honesto sem expor stack trace
(FR-008/FR-014). `try/catch` em torno do `fetch`+parse cobre os modos de falha.

---

## 7. Acessibilidade (piso mínimo — FR-015)

**Decision**: Usar um elemento `<button>` real (foco e Enter/Espaço nativos), `alt`
descritivo na imagem, contraste de texto AA no tema claro, `:focus-visible` estilizado, e
mensagens de estado em uma região com `role="status"`/`aria-live="polite"`.

**Rationale**: Tudo isso é nativo do HTML semântico, custo quase zero, e atende o piso sem
auditoria WCAG completa (que fica para a Fase 4).

---

## 8. Estrutura de pastas e reserva da Fase 2

**Decision**: Frontend na raiz; dados em `data/`; `scrapers/` criado **vazio** com um
`README.md` que documenta o contrato `{chef, site, titulo, url}` que os adaptadores futuros
deverão cumprir. Nenhum código Python é escrito nesta fase.

**Rationale**: Cumpre FR-011 (reservar espaço sem construir) e materializa a Separação
Estrita (Princípio IV) já na organização de diretórios.
