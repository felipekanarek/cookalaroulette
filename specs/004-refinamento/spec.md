# Feature Specification: Fase 4 — Refinamento (acessibilidade, responsividade, lançamento)

**Feature Branch**: `004-refinamento`
**Created**: 2026-06-05
**Status**: Draft
**Input**: User description: "Fase 4 — Refinamento do Cook à la Roulette: design final, responsividade e deploy público. O deploy já está no ar (GitHub Pages); resta a auditoria de acessibilidade (adiada da Fase 1), a verificação de responsividade pós-redesign, metadados sociais/SEO para compartilhamento, e metadados do repositório (LICENSE, descrição, homepage)."

## Clarifications

### Session 2026-06-05

- Q: O "deploy público" do briefing faz parte desta fase? → A: **Já feito** — o site está no ar via GitHub Pages (`felipekanarek.github.io/cookalaroulette/`). Esta fase é o **refino** em torno disso.
- Q: Esta fase mexe no scraper/dados? → A: **Não.** Só frontend + metadados do repositório (Separação Estrita — Princípio IV).
- Q: Qual licença do repositório? → A: **MIT** (permissiva, simples — padrão de facto para projeto de aprendizado/open source).
- Q: A "roleta de fontes" no clique entra nesta fase? → A: **Sim.** Ao clicar, a tipografia troca de fonte rapidamente por ~0,8s (efeito de roleta) antes do redirect, substituindo o fade — com fallback para `prefers-reduced-motion` (sem giro, transição mínima).
- Q: Qual imagem de prévia social? → A: **Gerar uma imagem própria on-brand** (texto-marca COOK À LA ROULETTE laranja sobre off-white, 1200×630).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Qualquer pessoa consegue usar (acessibilidade) (Priority: P1)

Uma pessoa que navega por teclado, usa leitor de tela, ou ativou "reduzir movimento" consegue
abrir o site, entender o que é, acionar o sorteio e chegar à receita — sem barreiras. O texto
permanece legível e com contraste suficiente, qualquer que seja a fonte sorteada.

**Why this priority**: Acessibilidade é a base de um lançamento público responsável; a auditoria
WCAG AA foi explicitamente adiada da Fase 1 para cá. Sem isso, parte do público é excluída.

**Independent Test**: Navegar o site usando só o teclado (Tab até o gatilho, Enter/Espaço para
acionar) com foco sempre visível; ativar "reduzir movimento" e confirmar que a animação não
dispara de forma incômoda; verificar com uma ferramenta de auditoria que os contrastes atendem
WCAG 2.1 AA; confirmar que um leitor de tela anuncia o propósito do gatilho e as mensagens de estado.

**Acceptance Scenarios**:

1. **Given** o site aberto, **When** a pessoa navega só por teclado, **Then** o gatilho recebe foco visível e é acionável por Enter/Espaço.
2. **Given** "prefers-reduced-motion" ativo, **When** a pessoa aciona o sorteio, **Then** não há animação que cause desconforto (transição mínima/instantânea), mas o redirecionamento ocorre.
3. **Given** qualquer fonte sorteada do Google Fonts, **When** a página carrega, **Then** o texto-marca permanece legível e com contraste WCAG AA (≥3:1 para texto grande); mensagens de estado (texto pequeno) atendem ≥4.5:1.
4. **Given** um leitor de tela, **When** a pessoa foca o gatilho, **Then** o propósito é anunciado de forma compreensível, e mudanças de estado (carregando/erro) são anunciadas.

---

### User Story 2 - Boa experiência em qualquer tela (responsividade) (Priority: P2)

A pessoa abre o site em celulares estreitos, tablets e desktops largos e, em todos, vê o
texto-marca **COOK À LA ROULETTE** bem composto, sem cortes nem rolagem horizontal.

**Why this priority**: O redesign tipográfico (tela cheia) precisa ser validado em telas reais —
"ROULETTE" é a palavra mais larga e pode estourar em telas estreitas. É um piso de qualidade
visível, mas a experiência já funciona; por isso P2.

**Independent Test**: Abrir o site em larguras de ~320px (celular pequeno) até desktop largo e
verificar que as três linhas aparecem centradas, sem corte e sem rolagem horizontal, em todas.

**Acceptance Scenarios**:

1. **Given** uma tela de ~320px de largura, **When** a página carrega, **Then** "COOK À LA ROULETTE" cabe sem rolagem horizontal e sem corte.
2. **Given** uma tela de desktop larga, **When** a página carrega, **Then** a composição permanece centrada e proporcional, ocupando a altura.

---

### User Story 3 - Link compartilhável e repositório apresentável (Priority: P3)

Quando alguém compartilha o link do site (WhatsApp, redes), aparece um preview com título,
descrição e imagem — convidativo. E quem chega ao repositório no GitHub entende o que é o
projeto (descrição, link do site, licença).

**Why this priority**: Aumenta alcance e credibilidade do lançamento, mas não afeta o uso do
produto em si; por isso P3.

**Independent Test**: Colar o link do site num validador de preview (ou app de mensagem) e ver
título, descrição e imagem; abrir o repositório e confirmar descrição, homepage apontando para o
site e um arquivo de licença.

**Acceptance Scenarios**:

1. **Given** o link do site colado num app que gera preview, **When** o preview é montado, **Then** mostra título, descrição e uma imagem de prévia coerentes com a marca.
2. **Given** o repositório no GitHub, **When** alguém o abre, **Then** há descrição, homepage (URL do site) e um arquivo de licença.

---

### Edge Cases

- **Fonte sorteada ilegível/estreita demais**: o conjunto de fontes deve ser curado para manter legibilidade; se uma fonte falhar ao carregar, cai para fonte de sistema legível (já previsto).
- **Tela muito estreita (<320px) ou fonte muito larga**: o dimensionamento deve evitar rolagem horizontal mesmo no pior caso (palavra "ROULETTE").
- **Crawler/preview sem JS**: as tags sociais ficam no HTML estático (não dependem de JS), então o preview funciona mesmo sem executar o sorteio.
- **Estados de vazio/erro no ar**: devem permanecer acessíveis (anunciados) e legíveis também na versão publicada.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O site MUST atender **WCAG 2.1 AA** no que se aplica a uma página de ação única: gatilho operável por teclado com foco visível, contraste AA (texto grande ≥3:1; texto pequeno ≥4.5:1), respeito a `prefers-reduced-motion`, e semântica/ARIA que permita a um leitor de tela anunciar o gatilho e as mudanças de estado.
- **FR-002**: O texto-marca MUST permanecer legível e com contraste AA **independentemente da fonte sorteada**; o conjunto de fontes MUST ser curado para legibilidade e MUST haver fallback de sistema legível.
- **FR-003**: O site MUST permanecer utilizável e bem composto de **~320px até desktop largo**, sem rolagem horizontal nem corte do texto-marca.
- **FR-004**: O documento MUST declarar idioma e título; e MUST incluir metadados de compartilhamento (Open Graph e Twitter Card) com título, descrição e **imagem de prévia**, no HTML estático (sem depender de JS).
- **FR-005**: A imagem de prévia social MUST ser um asset referenciado no `<head>` (não um elemento visível da página) — preservando o Minimalismo Radical (Princípio I): a tela continua só com o texto-marca.
- **FR-006**: O repositório público MUST ter um arquivo de **licença**, e MUST ter descrição e homepage (apontando para o site publicado).
- **FR-007**: Esta fase MUST NOT alterar o scraper, o `orquestrador.py`, o formato de dados (`receitas.json`) nem adicionar funcionalidades de produto (filtros/login/histórico permanecem proibidos). Mexe apenas no frontend e em metadados do repositório (Princípio IV).
- **FR-008**: Nenhum elemento visível permanente MUST ser adicionado à tela além do texto-marca (Princípio I) — melhorias de acessibilidade e metadados não introduzem UI nova visível.
- **FR-009**: Ao acionar o sorteio, o texto-marca MUST exibir uma "roleta de fontes" — trocar rapidamente de fonte por ~0,8s e então redirecionar (substitui o fade). A animação MUST ser não-interativa (não pede ação) e MUST respeitar `prefers-reduced-motion` (sem giro; transição mínima/instantânea), preservando o Zero Fricção (Princípio II) e o piso de acessibilidade.

### Key Entities *(include if feature involves data)*

- **Metadados sociais**: conjunto de tags no `<head>` (título, descrição, imagem de prévia, idioma) + a imagem de prévia em `assets/`. Não fazem parte do contrato de dados nem da UI visível.
- **Metadados do repositório**: licença, descrição e homepage do repositório no GitHub.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Uma auditoria de acessibilidade automatizada (padrão WCAG 2.1 AA) **não acusa violações** de contraste, nome/rótulo do gatilho, idioma ou foco; e o site é **100% operável só por teclado**.
- **SC-002**: Em telas de **320px a 1920px** de largura, **0 ocorrências** de rolagem horizontal ou texto cortado.
- **SC-003**: Com "reduzir movimento" ativo, a animação de clique **não dispara** (ou é instantânea), e o redirecionamento continua funcionando.
- **SC-004**: Em **100% das fontes** do conjunto curado, o contraste do texto-marca atende AA-large (≥3:1) e o texto permanece legível.
- **SC-005**: O link compartilhado exibe **título, descrição e imagem** de prévia em validadores de Open Graph/Twitter.
- **SC-006**: O repositório tem **licença, descrição e homepage** preenchidas; a homepage abre o site publicado.

## Assumptions

- **Deploy já concluído**: o site está no ar (GitHub Pages); esta fase refina, não re-publica.
- **Licença** (confirmado): **MIT**.
- **Imagem de prévia social** (confirmado): imagem própria on-brand, **1200×630**, com o texto-marca COOK À LA ROULETTE laranja sobre off-white. Formato rasterizado (PNG) para compatibilidade ampla com validadores de OG.
- **"Roleta de fontes" no clique** (confirmado: NO escopo): substitui o fade; ver FR-009. Reusa o mecanismo de fonte aleatória já existente; requer pré-carregar/alternar fontes do conjunto durante o giro.
- **Curadoria de fontes**: o conjunto atual do Google Fonts é revisado para remover qualquer fonte ilegível em tamanho grande; nenhuma fonte deve comprometer o contraste (cor preta/laranja sobre off-white já é alto contraste).
- **Sem novas dependências**: continua HTML/CSS/JS puro, sem build (Princípio VI).

## Out of Scope (Fase 4)

- Qualquer mudança no scraper, no orquestrador ou no formato de `receitas.json`.
- Funcionalidades de produto (filtros, login, perfil, histórico) — proibidas pela constituição.
- Automação de re-indexação via CI/cron (documentada como possibilidade futura na Fase 3).
- Domínio próprio/custom (o subdomínio do GitHub Pages é suficiente para o lançamento).
- (a "roleta de fontes" no clique foi promovida ao escopo — ver FR-009.)
