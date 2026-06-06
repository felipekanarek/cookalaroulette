<!--
SYNC IMPACT REPORT
==================
Version change: 1.0.0 → 2.0.0
Bump rationale: MAJOR — redefinição da regra concreta do Princípio I (Minimalismo
  Radical). O design pivotou de "uma imagem + um botão" para uma única tela
  tipográfica em que a página inteira é o gatilho do sorteio (texto-marca
  "COOK À LA ROULETTE"). Remover a exigência de imagem e mudar a superfície de ação
  é uma redefinição incompatível com a regra anterior → MAJOR. O intento do princípio
  (minimalismo radical, uma única ação) permanece intacto.

Modified principles:
  I.  Minimalismo Radical (UX) — regra concreta redefinida (tela tipográfica clicável)
  VI. Fundamentos sem Frameworks — esclarece que fontes via Google Fonts/CDN são permitidas

Added guidance:
  - Restrições Técnicas → "Identidade visual" (laranja #e85d29 sobre off-white;
    fonte aleatória do Google Fonts a cada visita)

Removed sections: none

Templates reviewed for alignment:
  ✅ .specify/templates/plan-template.md  — Constitution Check gate é genérico; sem edição
  ✅ .specify/templates/spec-template.md  — compatível
  ✅ .specify/templates/tasks-template.md — compatível
  ✅ .specify/templates/checklist-template.md — genérico; sem edição

Follow-up TODOs:
  ⚠ specs/001-fundacao-sorteio/spec.md — FR-001, FR-012 e a clarificação do rótulo do
    botão ("O que vou cozinhar?") ainda descrevem o design antigo; reconciliar a spec
    em seguida para alinhar com esta emenda.
  Projeto inicializado sem git (--no-git); não há workflow baseado em branches.
-->

# Cook à la Roulette Constitution

## Core Principles

### I. Minimalismo Radical (UX)

A interface MUST consistir de uma única tela em que a **página inteira é o gatilho do
sorteio**, exibindo apenas o nome **COOK À LA ROULETTE** em tipografia grande — nada
mais. É PROIBIDO adicionar à tela: filtros (culinária, tempo, dificuldade), lista de
Chefs, histórico de receitas, login, perfil, configuração, ou qualquer elemento
permanente além do texto-marca (mensagens transitórias de estado, como "carregando" ou
erro, são permitidas). Toda proposta de UI que acrescente um elemento permanente à
página principal MUST ser rejeitada salvo emenda explícita a esta constituição.

**Racional:** a aleatoriedade é o produto. Uma única superfície clicável, sem controles
nem escolhas, mantém a promessa — "o universo decide o que você vai cozinhar".

### II. Zero Fricção

O caminho do usuário MUST ser: abrir o site → clicar → ser redirecionado. NÃO MUST
existir cadastro, autenticação, onboarding, modal de consentimento de funcionalidade,
ou etapa intermediária entre o clique e o redirecionamento para a receita.

**Racional:** qualquer passo extra é atrito que mata a experiência de descoberta
instantânea.

### III. Redirecionar, Nunca Hospedar

O app MUST sempre enviar o usuário para a URL original da receita no site do Chef.
É PROIBIDO hospedar, copiar ou reexibir conteúdo dos Chefs — fotos, texto de receita,
ingredientes, modo de preparo ou vídeo. O produto é um **redirecionador e sorteador**,
nunca um agregador ou repositório de conteúdo.

**Racional:** respeito à autoria, ausência de responsabilidade sobre conteúdo de
terceiros, e fidelidade ao conceito de conectar pessoas ao conteúdo original.

### IV. Separação Estrita Scraper ↔ Frontend

O **scraper** (Python, executado offline ou agendado) e o **frontend** (navegador)
MUST ser componentes independentes. A ÚNICA fronteira de comunicação entre eles é o
arquivo `receitas.json`: o scraper o gera/atualiza; o frontend o lê. Nenhum dos dois
MUST conhecer detalhes de implementação do outro. Cada um MUST poder evoluir sem
exigir alteração no outro.

**Racional:** acoplamento baixo permite aprender e iterar cada lado isoladamente, e
é a espinha dorsal da arquitetura do projeto.

### V. Contrato Único dos Adaptadores

Cada Chef MUST ter um adaptador de scraping próprio (`scrapers/<site>.py`). Todo
adaptador, independentemente da técnica usada internamente, MUST retornar registros
no MESMO formato:

```json
{ "chef": "...", "site": "...", "titulo": "...", "url": "..." }
```

O orquestrador (`orquestrador.py`) MUST chamar todos os adaptadores e consolidar a
saída em `receitas.json`. Um adaptador NÃO MUST vazar formato específico do site para
fora de si mesmo.

**Racional:** um contrato estável desacopla o orquestrador e o frontend da
heterogeneidade dos sites de origem, permitindo crescer sem refatoração.

### VI. Fundamentos sem Frameworks

O frontend MUST ser HTML, CSS e JavaScript puro — sem frameworks de UI (React, Vue,
etc.) e sem etapa de build. Os dados MUST ser servidos como JSON simples lido
diretamente pelo navegador — sem banco de dados. Um serviço externo de fontes (Google
Fonts, carregado como folha de estilo via CDN) é PERMITIDO: é um stylesheet, não um
framework nem etapa de build. Bibliotecas no scraper limitam-se às ferramentas de
coleta (BeautifulSoup, Playwright, parser de sitemap).

**Racional:** o objetivo de aprendizado exige contato direto com os fundamentos da web
e do scraping, sem abstrações que escondam o que está acontecendo.

### VII. Aprendizado em Primeiro Lugar

Quando houver conflito entre velocidade de entrega e compreensão dos fundamentos, a
decisão MUST favorecer a opção que ensina mais (scraping, estrutura de projeto web,
HTTP, parsing). Atalhos que entregam resultado às custas de entendimento (ex.: copiar
uma solução pronta sem compreendê-la) SHOULD ser evitados.

**Racional:** este é declaradamente um projeto de aprendizado técnico; o aprendizado
é um objetivo de primeira classe, não um efeito colateral.

### VIII. Escala por Adição

Adicionar um novo Chef MUST significar apenas: criar um novo adaptador que respeita o
Contrato Único (Princípio V) e registrá-lo no orquestrador. Nenhuma adição de Chef
MUST exigir mudança na arquitetura, no formato de `receitas.json`, ou no frontend.

**Racional:** a curadoria cresce com o tempo; a arquitetura deve absorver crescimento
sem reescrita.

## Restrições Técnicas

**Stack obrigatória:**

| Camada | Tecnologia |
|--------|-----------|
| Scraper | Python + BeautifulSoup + Playwright |
| Dados | JSON (`receitas.json`) — sem banco de dados |
| Frontend | HTML + CSS + JavaScript puro — sem frameworks, sem build (fontes via Google Fonts/CDN permitidas) |

**Estratégia de coleta (ordem de preferência obrigatória):** para cada site, testar
nesta ordem até funcionar — (1) **Sitemap XML** (`dominio.com/sitemap.xml`, filtrando
URLs de receita); (2) **BeautifulSoup** (HTML server-side com estrutura consistente);
(3) **Playwright** (conteúdo carregado via JavaScript). Preferir sempre a técnica mais
simples que entregue o catálogo completo.

**Responsividade:** o frontend MUST funcionar bem em mobile e desktop.

**Identidade visual:** texto em **laranja (`#e85d29`)** sobre fundo **off-white**; a cada
visita uma **fonte é sorteada do Google Fonts**. A aleatoriedade tipográfica reforça o
conceito de "roleta" e o tom divertido do produto.

**Sorteio em duas etapas:** sortear um Chef → sortear uma receita indexada desse Chef
→ redirecionar para a URL original.

## Fluxo de Desenvolvimento

O projeto segue o fluxo **Spec Kit**: `constitution` → `specify` → (`clarify`) →
`plan` → `tasks` → (`analyze`) → `implement`. Cada fase do briefing (Fundação →
Scraper → Integração → Refinamento) é especificada e implementada como uma feature
distinta, na ordem das fases.

Toda feature nova MUST ser verificada contra estes princípios na etapa de planejamento
("Constitution Check" do `plan`). Itens **Fora do Escopo** do briefing (filtros, login,
histórico, hospedagem de conteúdo, app nativo, notificações, gamificação) MUST
permanecer fora até emenda explícita.

O projeto foi inicializado sem git (`--no-git`); não há workflow baseado em branches.

## Governance

Esta constituição prevalece sobre quaisquer outras práticas do projeto. Emendas MUST
ser documentadas neste arquivo, com versão e data atualizadas, e propagadas aos
templates dependentes (`plan`, `spec`, `tasks`).

**Política de versionamento (semântico):**
- **MAJOR** — remoção ou redefinição incompatível de um princípio ou regra de governança.
- **MINOR** — adição de novo princípio/seção ou expansão material de orientação.
- **PATCH** — esclarecimentos, correções de redação, refinamentos não semânticos.

Toda revisão de plano e implementação MUST verificar conformidade com os princípios.
Qualquer violação justificada (complexidade adicional, exceção temporária) MUST ser
explicitamente registrada e fundamentada no artefato correspondente.

**Version**: 2.0.1 | **Ratified**: 2026-06-05 | **Last Amended**: 2026-06-05
<!-- 2.0.1 (PATCH): correção de grafia da marca — "COOK À LA ROULETTE" (à, do francês "à la"). Sem mudança de regra. -->
