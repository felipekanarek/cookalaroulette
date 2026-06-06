# Feature Specification: Fase 3 — Integração e ampliação de cobertura

**Feature Branch**: `003-cobertura-chefs`
**Created**: 2026-06-05
**Status**: Draft
**Input**: User description: "Fase 3 — escalar a coleta automatizada para cobrir a curadoria completa de chefs do briefing (38 chefs / 25 países), resolvendo os dois padrões pendentes (sites sem sitemap e sites bloqueados) e definindo a cadência de re-indexação. Conexão scraper↔frontend e sorteio sobre dados coletados já estão feitos na Fase 2; o frontend permanece intocado."

## Clarifications

### Session 2026-06-05

- Q: Os objetivos "conectar scraper ao frontend" e "sorteio usar URLs indexadas" do briefing fazem parte desta fase? → A: **Não** — já foram entregues na Fase 2 (o frontend lê `data/receitas.json` gerado pelo scraper e o sorteio usa essas URLs). Esta fase é só **cobertura/dados**.
- Q: O frontend muda nesta fase? → A: **Não** (Princípio IV). Apenas o conjunto de adaptadores e os dados crescem.
- Q: Qual o alvo de cobertura desta fase? → A: **Todos os 38 chefs / 25 países** do briefing. Como o scraping é heterogêneo (alguns sites bloqueiam ou mudam), o critério de sucesso tolera falhas parciais (ver SC-001), mas a meta é a lista completa.
- Q: Qual a cadência de re-indexação? → A: **Manual sob demanda** (rodar `orquestrador.py` quando quiser atualizar); a estratégia de como agendar no futuro é documentada, mas a automação não é implementada nesta fase.
- Q: Qual técnica para sites sem sitemap? → A: **Listagem via BeautifulSoup primeiro**, recorrendo ao navegador real (Playwright) só quando a listagem depender de JavaScript (escalonamento, como sitemap→Playwright).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Descoberta com ampla diversidade cultural (Priority: P1)

A pessoa que volta ao site várias vezes é exposta a Chefs de muitos países e estilos —
não só os 3 da fase anterior. A roleta passa a sortear entre uma curadoria ampla,
cumprindo a promessa central do produto: descobrir culturas que ela não buscaria sozinha.

**Why this priority**: A diversidade cultural é o coração da proposta de valor. Sem
cobertura ampla, o produto entrega "aleatório", mas não "descoberta do mundo". É o que
esta fase existe para destravar.

**Independent Test**: Após uma rodada de coleta, abrir o site e realizar muitos sorteios,
verificando que aparecem receitas de Chefs de vários países diferentes (não apenas dos 3
da Fase 2), todas levando a páginas reais.

**Acceptance Scenarios**:

1. **Given** a coleta ampliada concluída, **When** a pessoa sorteia muitas vezes, **Then** ela encontra receitas de Chefs de múltiplos países além dos 3 iniciais.
2. **Given** o `data/receitas.json` ampliado, **When** o frontend é aberto, **Then** o sorteio funciona normalmente, sem nenhuma mudança no frontend (Princípio IV).

---

### User Story 2 - Coletar de sites sem sitemap (Priority: P2)

A pessoa que mantém o projeto consegue indexar receitas de Chefs cujos sites **não expõem
sitemap** (como a Panelinha), usando a leitura das páginas de listagem — sem que isso
exija uma arquitetura nova.

**Why this priority**: Vários sites da curadoria não têm sitemap; sem essa técnica, esses
Chefs (incluindo brasileiros) ficariam de fora — empobrecendo justamente a diversidade.
Mas a experiência (P1) já cresce com os sites que têm sitemap, então P2.

**Independent Test**: Rodar o adaptador de um site sem sitemap (ex.: Panelinha) e verificar
que ele retorna receitas reais no contrato `{chef, site, titulo, url}`, com URLs que
resolvem.

**Acceptance Scenarios**:

1. **Given** um site sem sitemap, **When** seu adaptador roda, **Then** ele coleta URLs de receita a partir das páginas de listagem, no mesmo contrato dos demais.
2. **Given** esse adaptador, **When** ele é adicionado, **Then** nenhum outro adaptador, o orquestrador ou o frontend precisa mudar (Escala por Adição — Princípio VIII).

---

### User Story 3 - Coletar de sites que bloqueiam bots (Priority: P3)

A pessoa que mantém o projeto consegue indexar Chefs cujos sites **bloqueiam scraping**
(como a Serious Eats, 403), reusando o fallback de navegador real já usado na Maangchi.

**Why this priority**: Alguns sites de peso bloqueiam; reusar o fallback Playwright os
recupera. É valioso, mas a maioria dos sites é coletável por sitemap/listagem, então P3.

**Independent Test**: Rodar o adaptador de um site bloqueado (ex.: Serious Eats) e verificar
que o fallback de navegador real recupera receitas; se ainda assim bloquear, o site é
reportado e pulado sem derrubar a coleta.

**Acceptance Scenarios**:

1. **Given** um site bloqueado, **When** seu adaptador roda, **Then** o fallback de navegador real é tentado e, em caso de sucesso, retorna receitas no contrato.
2. **Given** um site que bloqueia mesmo com o fallback, **When** a coleta roda, **Then** ele é reportado e pulado, e os demais Chefs continuam sendo coletados.

---

### Edge Cases

- **Site muda de estrutura entre rodadas**: o adaptador daquele site retorna menos/zero receitas e é reportado; os demais não são afetados.
- **Chef com site fora do ar**: reportado como erro/sem-receitas, sem abortar a rodada.
- **Receita aparece em mais de um Chef/site** (raro): deduplicação por URL evita repetição.
- **Coleta ampla demora**: aceitável (roda offline/sob demanda); o teto por site limita o volume.
- **Parte dos adaptadores falha**: a rodada conclui com os que funcionaram e relata os que não — nunca grava um `receitas.json` vazio (preserva o anterior).
- **Re-execução**: regenerar a curadoria não deve degradar a anterior em caso de falhas parciais.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST ampliar a coleta para cobrir Chefs adicionais da curadoria do briefing, além dos 3 já cobertos, mantendo todos no Contrato Único `{chef, site, titulo, url}`.
- **FR-002**: O sistema MUST suportar coletar de sites **sem sitemap**, lendo páginas de listagem para extrair URLs de receita — tentando BeautifulSoup primeiro e recorrendo ao navegador real apenas quando a listagem depender de JavaScript.
- **FR-003**: O sistema MUST suportar coletar de sites que **bloqueiam bots**, tentando um fallback de navegador real antes de pular o site.
- **FR-004**: As técnicas reutilizáveis (busca de sitemap via navegador; crawl de listagem) MUST ser compartilhadas, de modo que um novo adaptador não reescreva lógica comum (apenas declare seu padrão de URL e a técnica).
- **FR-005**: Adicionar um Chef MUST significar apenas criar seu adaptador e registrá-lo; nenhum outro adaptador, o orquestrador ou o frontend MUST precisar mudar (Princípio VIII).
- **FR-006**: Cada adaptador MUST coletar somente a localização da receita (chef, site, título, URL) — nunca o conteúdo (Princípio III).
- **FR-007**: O orquestrador MUST continuar consolidando, deduplicando por URL, verificando URLs vivas (tratando 403/401/429 como "existe, mas restringe bots" → válido) e gravando `data/receitas.json` de forma atômica, com relatório por site.
- **FR-008**: Uma falha isolada de um adaptador (bloqueio, mudança de estrutura, site fora do ar) MUST NOT abortar a coleta dos demais; deve ser registrada no relatório.
- **FR-009**: O sistema NÃO MUST modificar nenhum arquivo do frontend; sua única saída continua sendo `data/receitas.json` (Princípio IV).
- **FR-010**: O sistema MUST nunca sobrescrever `data/receitas.json` com um resultado vazio (preserva a curadoria anterior em caso de rodada totalmente falha).
- **FR-011**: A re-indexação MUST ser **manual sob demanda** (re-executar o orquestrador atualiza `data/receitas.json`), e o projeto MUST documentar como agendá-la no futuro (sem implementar automação nesta fase).
- **FR-012**: O relatório de execução MUST permitir ver a cobertura alcançada: por site, quantas receitas entraram e o que foi pulado/bloqueado/falhou (sem truncamento silencioso).

### Key Entities *(include if feature involves data)*

- **Adaptador de site**: a unidade que coleta de UM site, declarando seu padrão de URL e a técnica (sitemap / listagem / navegador real). Cresce em número ao longo da fase.
- **Registro de receita**: o contrato `{chef, site, titulo, url}` — inalterado desde a Fase 1.
- **Curadoria** (`data/receitas.json`): o conjunto consolidado, agora abrangendo muitos Chefs/países.
- **Relatório de cobertura**: resumo por site (técnica, coletadas, status) que evidencia a amplitude alcançada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A coleta MIRA os **38 Chefs / 25 países** do briefing; após uma rodada, `data/receitas.json` contém receitas de **pelo menos 25 Chefs** de **pelo menos 18 países diferentes** (tolerando que alguns sites bloqueiem/mudem de estrutura).
- **SC-002**: **100%** dos registros conformes ao contrato; **0 duplicatas**.
- **SC-003**: **Pelo menos 90%** das URLs coletadas levam a páginas reais (2xx, ou existentes mas restritas a bot).
- **SC-004**: Pelo menos **um** site sem sitemap e **um** site anteriormente bloqueado passam a contribuir receitas.
- **SC-005**: A falha de qualquer subconjunto de sites não reduz a coleta dos demais a zero, e nunca resulta em `receitas.json` vazio.
- **SC-006**: O frontend continua sorteando e redirecionando normalmente sobre a curadoria ampliada, **sem nenhuma alteração de código no frontend**.
- **SC-007**: A estratégia de re-indexação está documentada e é executável por quem mantém o projeto.

## Assumptions

- **Alvo de cobertura desta fase** (confirmado): **todos os 38 chefs / 25 países** do briefing. Entrega ainda pode ser organizada em lotes internamente, mas a meta da fase é a lista completa. Panelinha e Serious Eats entram primeiro (destravam as 2 técnicas que faltam).
- **Re-indexação** (confirmado): **manual sob demanda**; agendamento automático fica documentado como possibilidade futura, não implementado.
- **Técnica para sites sem sitemap** (confirmado): listagem via BeautifulSoup primeiro; navegador real (Playwright) só quando a listagem for renderizada por JavaScript.
- **Heterogeneidade**: cada site novo provavelmente exigirá ajuste fino do padrão de URL — é a natureza do scraping (Princípio VII, aprendizado).
- **Ordem de prioridade**: priorizar sites que ampliam a diversidade de países sobre adicionar mais receitas de países já cobertos.

## Out of Scope (Fase 3)

- Design visual final, responsividade refinada e **deploy público** — Fase 4.
- Qualquer mudança no frontend além de consumir o `data/receitas.json` ampliado.
- Agendamento automatizado de re-indexação (apenas documentar a estratégia; automação fica para depois, se desejado).
- Coleta de conteúdo de receita (sempre só localização — Princípio III).
