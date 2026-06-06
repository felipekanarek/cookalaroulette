# Feature Specification: Fase 2 — Scraper (indexação automatizada de receitas)

**Feature Branch**: `002-scraper-receitas`
**Created**: 2026-06-05
**Status**: Draft
**Input**: User description: "Fase 2 — Scraper do Cook à la Roulette: indexar automaticamente URLs de receitas dos sites dos Chefs e gerar/atualizar data/receitas.json no mesmo contrato {chef, site, titulo, url}, substituindo a curadoria manual da Fase 1. Adaptadores por Chef + orquestrador; técnicas em ordem (sitemap → BeautifulSoup → Playwright); coletar só a localização da receita, nunca o conteúdo; lidar com sites bloqueados. Experimento de aprendizado sobre ~5 sites."

## Clarifications

### Session 2026-06-05

- Q: O scraper deve baixar o conteúdo das receitas? → A: **Não.** Coleta apenas a localização (chef, site, título, URL); o conteúdo permanece na origem (Princípio III).
- Q: Cobrir quantos sites nesta fase? → A: **~5 sites** como experimento de aprendizado; os 38 são a Fase 3.
- Q: Quais 5 sites no experimento? → A: **Panelinha (Rita Lobo), Jamie Oliver, RecipeTin Eats (Nagi), Serious Eats (Kenji) e Maangchi** — mix que força as três técnicas, com a Maangchi como caso de site bloqueado (HTTP 403).
- Q: Quantas receitas coletar por site? → A: **Amostra com teto configurável por site** (padrão ~50/site); catálogo completo fica para a Fase 3.
- Q: O que fazer quando um site bloqueia a coleta (ex.: 403)? → A: **Tentar um fallback** (headers de navegador realistas / Playwright) **uma vez**; se persistir o bloqueio, **pular o site e registrar** no relatório (sem abortar a coleta dos demais).
- Q: Verificar se as URLs coletadas resolvem antes de gravar? → A: **Sim** — verificar cada URL (requisição leve HEAD/GET) e **descartar** as que não respondem 2xx antes de gravar, relatando quantas foram descartadas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gerar uma curadoria válida automaticamente (Priority: P1)

A pessoa que mantém o projeto roda um único comando e, ao final, o `data/receitas.json` é
(re)gerado automaticamente com URLs de receitas reais coletadas de um site de Chef — no
mesmo formato que o frontend já consome — sem que ela precise copiar URLs à mão.

**Why this priority**: É a espinha dorsal da fase: prova que o pipeline
"coletar → consolidar → escrever o contrato" funciona ponta a ponta. Com um único
adaptador já se substitui a curadoria manual por dados coletados, eliminando os links
quebrados que motivaram esta fase.

**Independent Test**: Rodar o orquestrador com um único adaptador configurado e verificar
que `data/receitas.json` é gerado, é um array conforme o contrato, e que abrir o frontend
em seguida sorteia e redireciona normalmente (sem mudar nada no frontend).

**Acceptance Scenarios**:

1. **Given** um adaptador configurado para um site, **When** a pessoa roda o orquestrador, **Then** `data/receitas.json` é escrito como um array de registros `{chef, site, titulo, url}` válidos.
2. **Given** o `data/receitas.json` recém-gerado, **When** o frontend é aberto, **Then** o sorteio funciona normalmente sobre os dados coletados (separação preservada — frontend não foi tocado).
3. **Given** uma coleta concluída, **When** a pessoa roda o orquestrador de novo, **Then** o arquivo é regenerado/atualizado de forma consistente (resultado idempotente para o mesmo estado dos sites).

---

### User Story 2 - Cobrir múltiplos sites com a técnica certa para cada um (Priority: P2)

A pessoa adiciona adaptadores para um conjunto representativo de ~5 sites, e cada adaptador
usa a técnica mais adequada àquele site — sitemap quando há, HTML estático quando o
conteúdo já vem pronto, ou navegador real quando o conteúdo carrega via JavaScript — todos
entregando o mesmo formato de registro.

**Why this priority**: É onde mora o aprendizado de scraping (o objetivo declarado da fase)
e onde se prova que a arquitetura de adaptadores absorve a heterogeneidade dos sites sem
quebrar o contrato. Mas o pipeline (P1) já entrega valor antes disso.

**Independent Test**: Rodar o orquestrador com os ~5 adaptadores e verificar que o
`data/receitas.json` final contém receitas de múltiplos Chefs/sites, todas no mesmo formato,
independentemente da técnica usada por cada adaptador.

**Acceptance Scenarios**:

1. **Given** adaptadores para sites com estruturas diferentes (com sitemap, HTML estático e conteúdo via JavaScript), **When** o orquestrador roda, **Then** todos contribuem registros no mesmo formato `{chef, site, titulo, url}`.
2. **Given** a estratégia de coleta por ordem de preferência, **When** um site oferece sitemap, **Then** o sitemap é a técnica usada (preferir a mais simples que entregue as receitas até o teto).
3. **Given** o resultado consolidado, **When** ele é inspecionado, **Then** cada registro indica corretamente o Chef e o site de origem.

---

### User Story 3 - Coleta robusta diante de bloqueios e erros (Priority: P3)

Quando um site bloqueia a coleta (proteção anti-bot) ou muda de estrutura, a coleta dos
demais sites continua; o que falhou é registrado de forma clara, e o resultado final não
contém duplicatas nem URLs inválidas.

**Why this priority**: Sustenta a confiabilidade e reflete um aprendizado real (a Maangchi
respondeu HTTP 403). É importante, mas o valor central (P1/P2) já existe sem o tratamento
completo de borda.

**Independent Test**: Rodar o orquestrador incluindo um site sabidamente bloqueado e
verificar que (a) os demais sites são coletados normalmente, (b) o site bloqueado é
reportado sem derrubar a execução, e (c) o arquivo final não tem duplicatas nem URLs
malformadas.

**Acceptance Scenarios**:

1. **Given** um site que bloqueia a coleta, **When** o orquestrador roda, **Then** ele registra o bloqueio e segue coletando os outros sites (não aborta tudo).
2. **Given** registros repetidos vindos de um mesmo site, **When** a saída é consolidada, **Then** duplicatas (mesma URL) são removidas.
3. **Given** a saída final, **When** ela é validada, **Then** todos os registros estão conformes ao contrato (campos não-vazios, URL `http(s)` absoluta).

---

### Edge Cases

- **Site bloqueia a coleta (HTTP 403 / anti-bot)**: registrar e pular o site sem abortar a coleta dos demais; opcionalmente tentar via navegador real (Playwright) antes de desistir.
- **Sitemap ausente ou inválido**: cair para a próxima técnica (HTML estático e, por fim, navegador real).
- **Estrutura do site mudou / nenhuma receita encontrada**: o adaptador retorna lista vazia e o orquestrador registra "0 receitas" para aquele site, sem quebrar.
- **URL coletada não resolve (link morto)**: verificar (HTTP) e **descartar** antes de gravar, para não reintroduzir links quebrados (FR-015).
- **Receita duplicada** (mesma URL repetida na fonte): deduplicar por URL.
- **Página de listagem/categoria capturada como se fosse receita**: filtrar para manter apenas URLs que sejam de receitas individuais.
- **Coleta parcial**: se a execução for interrompida, não deixar um `receitas.json` corrompido/meio-escrito (gravar de forma atômica).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST coletar, para cada site configurado, os dados de **localização** de receitas no formato de registro `{chef, site, titulo, url}` — e somente esses dados.
- **FR-002**: O sistema MUST NUNCA baixar, copiar ou armazenar o conteúdo das receitas (texto, ingredientes, modo de preparo, fotos, vídeo). Apenas a localização é indexada (Princípio III).
- **FR-003**: Cada site MUST ser coletado por um adaptador próprio e isolado; um orquestrador MUST acionar todos os adaptadores e consolidar a saída em `data/receitas.json`.
- **FR-004**: Todo adaptador MUST retornar registros no MESMO formato de contrato, independentemente da técnica interna usada (Contrato Único).
- **FR-005**: Para cada site, o sistema MUST tentar as técnicas de coleta na ordem de preferência — sitemap, depois HTML estático, depois navegador real — usando a mais simples que entregue as receitas até o teto por site (FR-014). Coletar o catálogo completo não é objetivo desta fase.
- **FR-006**: O sistema MUST produzir uma saída conforme o contrato existente (`contracts/receitas.schema.json` / o `receitas.schema.json` do projeto): array de objetos com `chef`, `site`, `titulo` e `url` não-vazios e `url` absoluta `http(s)`.
- **FR-007**: O sistema MUST remover registros duplicados (mesma URL) antes de gravar.
- **FR-008**: O sistema MUST excluir da saída URLs que não sejam de receitas individuais (ex.: páginas de categoria/listagem) e URLs malformadas.
- **FR-009**: Quando um site bloquear a coleta, o sistema MUST tentar um fallback (headers de navegador realistas / navegador real via Playwright) **uma vez**; se o bloqueio persistir, MUST pular o site e registrar a ocorrência, CONTINUANDO a coletar os demais (uma falha isolada não aborta a execução inteira).
- **FR-010**: O sistema MUST produzir um relatório de execução legível indicando, por site, quantas receitas foram coletadas e o que foi pulado/falhou (sem truncamento silencioso).
- **FR-011**: O sistema NÃO MUST modificar nenhum arquivo do frontend; sua única saída de dados é `data/receitas.json` (Separação Estrita — Princípio IV).
- **FR-012**: Rodar o sistema novamente MUST regenerar/atualizar `data/receitas.json` de forma consistente para o mesmo estado dos sites (idempotência), e a gravação MUST ser atômica (sem deixar arquivo parcial em caso de interrupção).
- **FR-013**: Adicionar um novo site MUST significar apenas criar um novo adaptador que respeita o contrato e registrá-lo no orquestrador — sem alterar os demais adaptadores, o formato de saída ou o frontend (Escala por Adição — Princípio VIII).
- **FR-014**: Cada adaptador MUST respeitar um **teto configurável de receitas por site** (padrão ~50); ao atingir o teto, para de coletar daquele site. Coletar o catálogo completo é Fase 3.
- **FR-015**: Antes de gravar, o sistema MUST verificar que cada URL coletada resolve (resposta HTTP 2xx via requisição leve) e MUST descartar da saída as que não resolverem, registrando no relatório quantas foram descartadas.

### Key Entities *(include if feature involves data)*

- **Adaptador de site**: a unidade que sabe coletar receitas de UM site. Conhece a técnica adequada àquele site e produz registros no contrato comum. Identificado pelo site/Chef que cobre.
- **Registro de receita**: a unidade de saída — `{chef, site, titulo, url}`. É o mesmo contrato consumido pelo frontend e definido em `receitas.schema.json` (forma estável compartilhada entre todas as fases).
- **Relatório de execução**: o resumo de uma rodada do orquestrador — por site: quantas receitas coletadas, quais foram puladas/bloqueadas/falharam. Não persiste no contrato; serve à observabilidade da coleta.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Após uma rodada, `data/receitas.json` é gerado contendo receitas de **pelo menos 3 sites** diferentes, totalizando **pelo menos 30 receitas** reais.
- **SC-002**: **100%** dos registros gravados estão conformes ao contrato (campos não-vazios, `url` absoluta `http(s)`).
- **SC-003**: **0 duplicatas** (URLs repetidas) no arquivo final.
- **SC-004**: **Pelo menos 90%** das URLs coletadas resolvem (respondem HTTP 2xx) quando verificadas — substituindo de fato os links quebrados da Fase 1.
- **SC-005**: A presença de um site bloqueado **não reduz a zero** a coleta dos demais — os outros sites continuam sendo indexados.
- **SC-006**: Abrir o frontend após a coleta sorteia e redireciona normalmente, **sem nenhuma alteração no código do frontend**.
- **SC-007**: O relatório de execução permite saber, para cada site, quantas receitas entraram e o que foi pulado — sem que nada seja descartado silenciosamente.

## Assumptions

- **Conjunto de 5 sites do experimento** (confirmado): *Rita Lobo (panelinha.com.br)*, *Jamie Oliver (jamieoliver.com)*, *Nagi Maehashi (recipetineats.com)*, *Kenji López-Alt (seriouseats.com)* e *Maangchi (maangchi.com)* — escolhido para forçar as três técnicas, com a Maangchi como caso de site bloqueado (HTTP 403 observado nesta sessão).
- **Volume por site** (confirmado): coletar uma **amostra com teto configurável por site** (padrão ~50 receitas/site); o catálogo completo não é objetivo desta fase (Fase 3).
- **Site bloqueado** (confirmado): tentar **um fallback** (headers realistas / Playwright) e, se persistir, **pular e registrar**; não é objetivo desta fase contornar agressivamente proteções anti-bot.
- **Re-indexação**: a coleta roda **sob demanda / manualmente** nesta fase; agendamento automático e cadência de atualização ficam fora do escopo (decidíveis depois).
- **Cortesia de coleta**: respeitar boas práticas (ritmo de requisições moderado, identificar-se via user-agent); o objetivo é aprendizado, não sobrecarregar os sites de terceiros.
- **Idioma e ambiente**: scripts executados localmente pela pessoa mantenedora; saída única em `data/receitas.json`.

## Out of Scope (Fase 2)

- Cobrir todos os 38 sites do briefing — Fase 3.
- Agendamento automático de re-indexação e definição de cadência.
- Qualquer mudança no frontend (já consome o contrato) — Fase 3/4.
- Design visual e deploy público — Fase 4.
- Contornar agressivamente proteções anti-bot (CAPTCHAs, rotação de IP, etc.).
- Armazenar qualquer conteúdo de receita além de chef/site/título/URL.
