# Feature Specification: Fase 1 — Fundação (sorteio e redirecionamento)

**Feature Branch**: `001-fundacao-sorteio`
**Created**: 2026-06-05
**Status**: Draft
**Input**: User description: "Fase 1 — Fundação do Cook à la Roulette: estrutura inicial do projeto, frontend estático de página única (imagem + botão), lista de Chefs e receitas em arquivo de dados com URLs hardcoded, e sorteio em duas etapas que redireciona o usuário para a receita original. Objetivo: validar a experiência de descoberta ponta a ponta antes de construir o scraper."

## Clarifications

### Session 2026-06-05

> ⚠️ As decisões sobre **rótulo do botão ("O que vou cozinhar?"), tagline e mood ("claro
> e arejado")** abaixo foram **superadas** pela sessão "Redesign tipográfico" mais adiante.
> As demais (tolerância ±10%, cliques durante a animação, falha de carregamento, piso de
> acessibilidade) seguem válidas.

- Q: Ao clicar no botão, o que acontece antes do redirecionamento? → A: Uma **animação breve de roleta** (~0,8s) sugerindo o sorteio, e então o redirecionamento. A animação é **não-interativa**: não exige nenhuma ação nem decisão da pessoa, é apenas uma transição. Por isso permanece compatível com o princípio de Zero Fricção (não introduz "etapa" de decisão).
- Q: Qual o texto do botão de ação (CTA)? → A: **"O que vou cozinhar?"**
- Q: A tagline "o universo decide o que você vai cozinhar hoje" aparece na tela? → A: **Não.** A tela mostra apenas imagem + botão (minimalismo radical, interpretação literal).
- Q: Qual a direção visual (mood) da tela? → A: **Claro e arejado** — fundo claro, muito espaço em branco, minimalismo de inspiração escandinava.
- Q: Qual a tolerância concreta para considerar o sorteio entre Chefs "equilibrado" (SC-003 / US2)? → A: Cada Chef deve ficar dentro de **±10%** da frequência esperada (1 / nº de Chefs) ao longo de **≥1000 sorteios** simulados.
- Q: O que acontece se a pessoa clicar no botão de novo enquanto a animação de roleta está rodando? → A: **Ignorar** os cliques extras — o botão fica desabilitado durante a animação e volta a aceitar cliques após o redirecionamento.
- Q: O que acontece se a fonte de dados de receitas falhar ao carregar (arquivo ausente, JSON malformado)? → A: Exibir uma **mensagem amigável distinta** ("não foi possível carregar as receitas agora"), diferente da mensagem de lista vazia e sem expor erro técnico.
- Q: Qual o piso de acessibilidade na Fase 1? → A: **Piso mínimo** — botão acionável por teclado (Enter/Espaço) e com foco visível, imagem com texto alternativo, contraste de texto WCAG 2.1 AA (≥ 4.5:1). Auditoria WCAG AA completa fica para a Fase 4.

### Session 2026-06-05 — Redesign tipográfico (supera decisões anteriores de UI)

> Após validar a experiência, o design foi repensado para um visual tipográfico e
> divertido. As decisões abaixo **substituem** as anteriores sobre imagem, rótulo do
> botão e mood. Refletido na constituição v2.0.0 (Princípio I).

- Q: Como fica a tela principal? → A: **Sem ilustração.** A **tela inteira é clicável** (não há mais um botão isolado), exibindo o nome **COOK À LA ROULETTE** em tipografia grande, em três linhas ocupando toda a altura. (Supera o "imagem + botão 'O que vou cozinhar?'".)
- Q: Cores? → A: Texto em **laranja `#e85d29`** sobre fundo **off-white**. (Supera o mood "claro e arejado escandinavo" — agora o tom é divertido.)
- Q: Tipografia? → A: A cada visita, uma **fonte é sorteada do Google Fonts** (pool de famílias display variadas), reforçando o conceito de "roleta".
- Q: O que acontece no clique? → A: Mantém-se uma **animação breve não-interativa (~0,8s)** — agora um fade discreto da tela — seguida do redirecionamento. (FR-005/FR-013 seguem válidos.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Sortear uma receita e ir cozinhar (Priority: P1)

Uma pessoa sem ideia do que cozinhar abre o site, vê uma tela tipográfica com o nome
**COOK À LA ROULETTE** em letras grandes (e uma fonte diferente a cada visita). Clica
em qualquer lugar da tela e é imediatamente levada a uma receita real, escolhida ao
acaso, no site original de um Chef curado. Ela não precisa escolher nada, não cria
conta e não configura filtros — o universo decide por ela.

**Why this priority**: É a essência do produto. Sem isso, não há nada. Entrega sozinha
toda a proposta de valor ("o universo decide o que você vai cozinhar hoje") e valida a
experiência de descoberta ponta a ponta com dados hardcoded, antes de qualquer scraper.

**Independent Test**: Abrir o site, clicar no botão e verificar que o navegador chega a
uma página de receita real e funcional no domínio de um Chef da lista. Repetir alguns
cliques e verificar que receitas diferentes aparecem.

**Acceptance Scenarios**:

1. **Given** o site aberto com a lista de receitas curadas carregada, **When** a pessoa clica em qualquer lugar da tela, **Then** uma animação breve é exibida e, ao terminar, ela é redirecionada para a URL original de uma receita de um Chef da lista — sem nenhuma etapa de confirmação no meio.
2. **Given** a pessoa acabou de ser redirecionada para uma receita, **When** ela volta ao site e clica novamente, **Then** um novo sorteio é feito e ela pode chegar a uma receita diferente.
3. **Given** o site aberto, **When** a página termina de carregar, **Then** a pessoa vê apenas o texto-marca COOK À LA ROULETTE — nenhum filtro, lista de chefs, campo de login ou configuração.

---

### User Story 2 - Descoberta equilibrada entre Chefs (Priority: P2)

A pessoa que volta várias vezes ao site é exposta a Chefs de diferentes países e
estilos, e não fica presa ao Chef que por acaso tem mais receitas cadastradas. A
diversidade cultural é parte do valor da descoberta.

**Why this priority**: Diferencia "descoberta" de "aleatório enviesado". Um sorteio
ingênuo sobre todas as receitas favoreceria Chefs com catálogos maiores; o sorteio em
duas etapas (primeiro o Chef, depois a receita) dá a cada Chef a mesma chance. É
importante, mas a experiência básica (P1) já entrega valor sem isso.

**Independent Test**: Com a lista contendo Chefs que têm quantidades diferentes de
receitas, executar ≥1000 sorteios e verificar que cada Chef é selecionado dentro de
±10% da frequência esperada (1 / nº de Chefs), independentemente de quantas receitas
possui.

**Acceptance Scenarios**:

1. **Given** uma lista com Chefs que têm números diferentes de receitas, **When** muitos sorteios são realizados, **Then** cada Chef tem aproximadamente a mesma chance de ser escolhido (sorteio do Chef independe do tamanho do seu catálogo).
2. **Given** um Chef selecionado no sorteio, **When** a receita é sorteada, **Then** ela pertence exclusivamente àquele Chef.

---

### User Story 3 - Experiência sofisticada em qualquer tela (Priority: P3)

A pessoa acessa o site tanto pelo celular quanto pelo computador e, em ambos, encontra
uma tela tipográfica bem composta — o texto-marca centrado, legível e ocupando a
altura, sem aparência de "sorteador de bingo".

**Why this priority**: Sustenta a percepção de sofisticação e a usabilidade mobile, mas
o fluxo de descoberta (P1) funciona mesmo antes do polimento visual final (que é a
Fase 4). É um piso de qualidade, não o coração da feature.

**Independent Test**: Abrir o site em uma largura de tela móvel e em uma de desktop e
verificar que o texto-marca permanece centrado, legível e clicável, sem
quebra de layout nem rolagem horizontal.

**Acceptance Scenarios**:

1. **Given** o site aberto em uma tela estreita (celular), **When** a página carrega, **Then** o texto-marca aparece centrado, sem corte e sem rolagem horizontal.
2. **Given** o site aberto em uma tela larga (desktop), **When** a página carrega, **Then** a composição permanece centrada e proporcional, com a tela inteira clicável.

---

### Edge Cases

- **Lista de receitas vazia**: se a fonte de dados não tiver nenhuma receita, o botão não deve quebrar silenciosamente — a pessoa deve receber uma indicação clara de que não há receitas no momento (sem expor erro técnico).
- **Chef sem receitas**: um Chef cadastrado sem nenhuma receita nunca deve ser o resultado de um sorteio (não pode levar a um beco sem saída).
- **URL indisponível na origem**: se a página da receita no site do Chef estiver fora do ar, isso está fora do controle do app; o app cumpre seu papel ao redirecionar para a URL correta. (Verificação de links é tratada em fases posteriores.)
- **Sorteio repetido**: dois cliques seguidos podem, por acaso, levar à mesma receita — comportamento aceitável nesta fase (não há histórico nem dedup, por minimalismo).
- **Dado de receita malformado**: um registro sem URL válida não deve ser oferecido como resultado de sorteio.
- **Falha ao carregar os dados**: se a fonte de dados não puder ser lida ou estiver corrompida (JSON malformado), a pessoa vê uma mensagem amigável distinta da de lista vazia, sem erro técnico (ver FR-014).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST apresentar uma página única em que a **tela inteira é o gatilho do sorteio**, exibindo apenas o texto-marca **COOK À LA ROULETTE** em tipografia grande (três linhas ocupando a altura), sem nenhum outro elemento permanente e sem tagline ou texto explicativo (sem filtros, lista de Chefs, histórico, login ou configuração). Mensagens transitórias de estado (carregando/erro) são permitidas.
- **FR-002**: O sistema MUST carregar a curadoria de Chefs e receitas a partir de uma fonte de dados editável manualmente, em que cada receita é descrita por: nome do Chef, site de origem, título da receita e URL original.
- **FR-003**: Ao acionar o botão, o sistema MUST selecionar uma receita ao acaso em duas etapas — primeiro sorteando um Chef entre os disponíveis, depois sorteando uma receita pertencente a esse Chef.
- **FR-004**: O sorteio do Chef MUST ser independente da quantidade de receitas que cada Chef possui (cada Chef com ao menos uma receita tem a mesma probabilidade de ser escolhido).
- **FR-005**: Após o clique, o sistema MUST exibir uma animação breve (~0,8s — um fade discreto da tela) e então redirecionar a pessoa para a URL original da receita selecionada. A animação MUST ser não-interativa (não exige clique, escolha ou confirmação) e MUST NOT introduzir qualquer etapa de decisão entre o clique inicial e o redirecionamento.
- **FR-006**: O sistema MUST nunca hospedar, copiar ou reexibir o conteúdo das receitas (texto, ingredientes, fotos, vídeo) — apenas redirecionar para a origem.
- **FR-007**: O sistema MUST excluir do sorteio Chefs sem receitas e receitas sem URL válida, de modo que todo resultado de sorteio leve a uma URL utilizável.
- **FR-008**: Quando não houver nenhuma receita disponível, o sistema MUST comunicar isso de forma compreensível para a pessoa, sem expor mensagem de erro técnica.
- **FR-009**: A página MUST permanecer utilizável e bem composta tanto em telas de celular quanto de desktop, mantendo o texto-marca centrado, legível e ocupando a altura da tela, sem rolagem horizontal.
- **FR-010**: A pessoa MUST conseguir realizar um novo sorteio facilmente após retornar ao site, sem recarregar manualmente nem refazer qualquer configuração.
- **FR-011**: A organização inicial do projeto MUST separar claramente a parte visível ao usuário (a página) da fonte de dados de receitas, e MUST reservar espaço para os componentes de coleta de receitas das fases seguintes, sem que estes sejam construídos nesta fase.
- **FR-012**: A direção visual MUST ser tipográfica e divertida: texto em **laranja `#e85d29`** sobre fundo **off-white**, com o nome em letras grandes ocupando a tela.
- **FR-016**: A cada visita, o sistema MUST escolher aleatoriamente uma fonte de um conjunto de famílias do Google Fonts e aplicá-la ao texto-marca, reforçando o conceito de "roleta". Se a fonte não carregar, o sistema MUST cair para uma fonte de sistema legível (degradação graciosa).
- **FR-013**: Durante a animação de roleta, o sistema MUST ignorar cliques adicionais no botão (botão desabilitado), evitando sorteios concorrentes ou redirecionamento duplicado; o botão volta a aceitar cliques após o redirecionamento.
- **FR-014**: Quando a fonte de dados de receitas falhar ao carregar (arquivo ausente, conteúdo malformado ou erro de leitura), o sistema MUST exibir uma mensagem amigável **distinta** da mensagem de lista vazia ("não foi possível carregar as receitas agora"), sem expor mensagem de erro técnica.
- **FR-015**: A página MUST atender a um piso mínimo de acessibilidade: o gatilho (a tela clicável) MUST ser acionável por teclado (Enter/Espaço) e exibir foco visível; o texto-marca, por ser grande, MUST atender contraste **WCAG 2.1 AA para texto grande** (≥ 3:1) e qualquer mensagem de estado (texto pequeno) MUST atender **≥ 4.5:1**. (Auditoria WCAG AA completa da interface fica para a Fase 4.)

### Key Entities *(include if feature involves data)*

- **Receita curada**: a unidade que pode ser sorteada. Atributos: **Chef** (nome de quem assina), **site** (domínio de origem), **título** (nome da receita), **URL** (endereço original e completo da receita). Esta é a forma de registro estável que todas as fases do projeto compartilham.
- **Chef**: quem assina um conjunto de receitas. Identificado pelo nome e associado a um site de origem. Agrupa uma ou mais Receitas curadas; é a primeira coisa sorteada no processo de duas etapas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A partir da abertura do site, a pessoa consegue chegar a uma receita real em no máximo 1 clique.
- **SC-002**: 100% dos sorteios levam a uma URL de receita pertencente a um Chef da curadoria (nenhum beco sem saída, nenhuma URL inválida).
- **SC-003**: Ao longo de ≥1000 sorteios simulados, cada Chef é selecionado dentro de ±10% da frequência esperada (1 / nº de Chefs), independentemente do tamanho do seu catálogo — o tamanho do catálogo não aumenta a chance de um Chef ser escolhido.
- **SC-004**: A pessoa percebe e usa a página sem instruções, em telas de celular e desktop, sem encontrar rolagem horizontal ou elementos cortados.
- **SC-005**: A página principal não apresenta nenhum elemento além do texto-marca COOK À LA ROULETTE (verificável por inspeção visual direta).
- **SC-006**: A curadoria inicial cobre múltiplos Chefs de mais de um país, validando que a diversidade cultural da descoberta é perceptível já nesta fase.
- **SC-007**: A pessoa consegue acionar o sorteio usando apenas o teclado (foco visível + Enter/Espaço) — verificável sem ferramentas além do navegador.

## Assumptions

- **Curadoria mínima da fase**: a fonte de dados é populada manualmente com pelo menos 3 Chefs de países diferentes, cada um com pelo menos 3 receitas reais, totalizando o suficiente para perceber variedade. URLs apontam para receitas reais e ativas no momento da curadoria.
- **Destino do redirecionamento**: o redirecionamento abre a receita em uma nova aba, preservando o site da roleta na aba original para que a pessoa possa sortear de novo facilmente (apoia FR-010 e o ciclo de descoberta). Caso o navegador bloqueie a nova aba, a navegação ocorre na própria aba.
- **Sem memória entre sorteios**: não há histórico nem prevenção de repetição imediata — coerente com o princípio de minimalismo radical e ausência de histórico.
- **Identidade tipográfica**: não há ilustração; a identidade é o texto-marca COOK À LA ROULETTE em laranja sobre off-white, com fonte sorteada do Google Fonts a cada visita. O refinamento estético final é tratado na Fase 4.
- **Sem coleta automatizada nesta fase**: nenhuma indexação automática (scraper) é construída agora; toda a curadoria é manual e serve para validar a experiência. O scraper é a Fase 2.
- **Idioma da interface**: português, coerente com o público inicial do projeto.

## Out of Scope (Fase 1)

- O scraper e o orquestrador (construção de coleta automatizada) — Fase 2.
- Substituição das URLs hardcoded por URLs indexadas automaticamente — Fase 3.
- Design visual final e deploy público — Fase 4.
- Qualquer filtro (culinária, tempo, dificuldade), login, perfil, histórico, notificações ou gamificação — fora do escopo do produto por enquanto.
- Verificação automática de links quebrados na origem.
