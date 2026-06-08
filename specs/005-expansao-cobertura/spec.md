# Feature Specification: Expansão de Cobertura (Lista 2)

**Feature Branch**: `005-expansao-cobertura`  
**Created**: 2026-06-08  
**Status**: Draft  
**Input**: User description: "Fase 5 — Expansão de Cobertura (Lista 2): adicionar ~58 novos sites de chefs/marcas ao scraper, ampliando países e categorias (inclui coquetéis e editoriais), no contrato {chef, site, titulo, url}."

## Clarifications

### Session 2026-06-08

- Q: Qual a meta de escopo desta fase (Lista 2)? → A: Tentar TODOS os ~58 sites, em lotes paralelos; sites bloqueados/mortos são documentados, não bloqueiam a fase.
- Q: Os sites de coquetéis (Liquor.com, Punch, Difford's Guide) entram nesta fase? → A: Sim — incluídos no mesmo catálogo e contrato {chef, site, titulo, url}.
- Q: Como preencher o campo `chef` de sites editoriais/de marca? → A: Usar o nome da marca no campo `chef` (ex.: "GialloZafferano", "The Kitchn", "Great British Chefs").
- Q: Critério mínimo para "site integrado com sucesso" (SC-001)? → A: ≥ 10 receitas válidas e vivas por site.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mais chefs e países no sorteio (Priority: P1)

Como visitante do Cook à la Roulette, ao clicar quero ser redirecionado para receitas de uma
variedade muito maior de cozinheiros e países do mundo — não só os 30 atuais, mas dezenas de
novos (Peru, Colômbia, Chile, Canadá, Marrocos, Líbano, China, Coreia, etc.), incluindo
marcas editoriais reconhecidas e até coquetéis.

**Why this priority**: É o coração desta fase e o que entrega valor direto ao produto (a
aleatoriedade fica mais rica). Cada site novo integrado já aumenta a variedade do sorteio.

**Independent Test**: Para cada site da Lista 2 com adaptador criado, rodar `coletar(10)`
isoladamente retorna ≥1 registro válido no contrato {chef, site, titulo, url} apontando para
uma página de receita real e viva daquele site.

**Acceptance Scenarios**:

1. **Given** um site novo da Lista 2 com adaptador implementado e registrado, **When** rodo
   `python3 orquestrador.py --site <modulo> --limite N`, **Then** as receitas daquele site são
   mescladas ao catálogo, os demais chefs (Lista 1) são preservados, e o relatório mostra a
   contagem coletada para aquele site.
2. **Given** o catálogo após integrar a Lista 2, **When** o frontend sorteia, **Then** ele pode
   redirecionar para receitas dos novos chefs/marcas exatamente como faz com os existentes
   (sem nenhuma mudança no frontend nem no contrato de dados).

---

### User Story 2 - Sites difíceis tratados com a técnica certa (Priority: P2)

Como mantenedor do scraper, preciso que sites que exigem navegador (JS) ou que estão atrás de
proteção (Cloudflare/verificação) sejam coletados pela técnica adequada, de forma legítima,
sem evadir proteções e sem quebrar a rodada dos demais.

**Why this priority**: Boa parte da Lista 2 tem dicas de "requer Playwright" ou "bloqueado na
verificação". Sem tratar isso, esses sites simplesmente não entram.

**Independent Test**: Para um site marcado "requer Playwright", o adaptador usa a técnica de
navegador e `coletar(10)` retorna receitas; para um site "bloqueado na verificação", as URLs
coletadas são preservadas porque `url_viva` trata 403/429 como página existente.

**Acceptance Scenarios**:

1. **Given** um site que bloqueia o cliente HTTP mas serve humanos, **When** o adaptador coleta
   e o orquestrador verifica URLs, **Then** as receitas não são descartadas (403/429 = viva).
2. **Given** um site totalmente atrás de Cloudflare, **When** nenhuma técnica direta funciona,
   **Then** a coleta usa o Internet Archive (wayback) para descobrir a localização das receitas,
   sem contornar a proteção do site original.

---

### User Story 3 - Integração incremental e prestação de contas honesta (Priority: P3)

Como mantenedor, quero integrar os sites em lotes (sem re-raspar tudo) e ter um registro claro
de quais sites entraram, quantas receitas cada um trouxe, e quais ficaram de fora (bloqueados,
mortos, sem receitas) e por quê.

**Why this priority**: Garante que a expansão seja gerenciável, reversível por site e honesta
sobre o que não foi possível — evitando a falsa impressão de cobertura total.

**Independent Test**: Após uma rodada `--site` de um lote, o relatório por site lista cada
adaptador com status (ok / sem-receitas / bloqueado-pulado / erro), e o catálogo reflete só os
sites bem-sucedidos somados aos já existentes.

**Acceptance Scenarios**:

1. **Given** um site da Lista 2 que se revela morto ou totalmente inacessível, **When** tento
   integrá-lo, **Then** ele é documentado como não-integrado (com motivo) e NÃO derruba os demais.
2. **Given** um adaptador que coletou 0 numa rodada `--site`, **When** a mesclagem ocorre,
   **Then** as receitas anteriores daquele site (se houver) são preservadas (anti-vazio por site).

---

### Edge Cases

- **Site morto / domínio fora do ar**: documentado como não-integrado; não conta como falha da fase.
- **Sitemap poluído** (posts de mídia, institucional misturados): o filtro `_e_receita` exclui
  não-receitas; quando o sitemap não distingue, usar crawl/listagem de páginas de receita.
- **Site que muda para app JS** (sem links no HTML cru): usar técnica de navegador (Playwright).
- **Coquetéis vs comida**: tratados no mesmo catálogo e contrato (são "o que você vai preparar").
- **Marca sem chef individual** (editorial): o nome da marca ocupa o campo `chef`.
- **Sobreposição com a Lista 1**: nenhum site da Lista 2 deve duplicar um já existente; a
  deduplicação por URL do orquestrador protege contra registros repetidos.
- **Rate-limit no lote** (técnica crawl frágil): adaptador tolerante a 429 / fallback de técnica,
  ou recuperação posterior via `--site`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST ter um adaptador Python dedicado por site da Lista 2, em
  `scrapers/<site>.py`, expondo `CHEF`, `SITE`, `TECNICAS` e `coletar(limite)`.
- **FR-002**: Cada adaptador MUST produzir registros no contrato existente
  `{chef, site, titulo, url}`, sem alterar o contrato.
- **FR-003**: Cada adaptador MUST coletar APENAS a localização (URL) das receitas — nunca o
  conteúdo da receita.
- **FR-004**: Cada adaptador MUST escolher a técnica mais simples que funciona (sitemap →
  sitemap-via-navegador → crawl/listagem → wayback), com filtro de URL de receita.
- **FR-005**: Sites que exigem navegador (JS) MUST ser coletados via técnica de navegador
  (Playwright); sites totalmente bloqueados (Cloudflare) MUST usar wayback (descoberta via
  Internet Archive), sem evadir proteções.
- **FR-006**: A verificação de URL viva MUST tratar 403/429 como "página existe" (viva), pois o
  app redireciona um humano cujo navegador acessa normalmente.
- **FR-007**: Cada adaptador novo MUST ser registrado no `orquestrador.py` (import + lista
  `ADAPTADORES`) — adicionar site = um arquivo + um registro.
- **FR-008**: A integração ao catálogo MUST poder ocorrer por site/lote via modo cirúrgico
  `--site`, MESCLANDO no `data/receitas.json` e preservando todos os chefs já existentes (Lista 1).
- **FR-009**: O processo MUST produzir um relatório por site com status (ok / sem-receitas /
  bloqueado-pulado / erro) e a contagem coletada.
- **FR-010**: Sites editoriais/de marca sem chef individual MUST usar o nome da marca no campo
  `chef` (ex.: "GialloZafferano", "The Kitchn", "Great British Chefs").
- **FR-011**: Receitas de coquetéis (Liquor.com, Punch, Difford's Guide) MUST entrar no mesmo
  catálogo e contrato das demais receitas.
- **FR-012**: A fase MUST NÃO modificar o frontend, o algoritmo de sorteio nem o contrato de dados
  (Separação Estrita — Princípio IV).
- **FR-013**: A fase MUST NÃO duplicar sites já presentes na Lista 1; a deduplicação por URL
  normalizada do orquestrador permanece ativa.
- **FR-014**: Sites não-integráveis (mortos, inacessíveis) MUST ser documentados com o motivo, sem
  derrubar a integração dos demais (falha isolada).

### Key Entities *(include if feature involves data)*

- **Adaptador de site**: módulo Python por site; entrada = limite; saída = lista de registros de
  receita. Atributos: CHEF (nome do chef/marca), SITE (domínio), TECNICAS (técnicas usadas).
- **Registro de receita**: `{chef, site, titulo, url}` — a unidade do catálogo (inalterada).
- **Catálogo** (`data/receitas.json`): lista de registros consumida pelo frontend; cresce com a
  Lista 2 via mesclagem cirúrgica, preservando a Lista 1.
- **Relatório de coleta**: por site, status + contagem; base da prestação de contas honesta.

### Lista 2 — Sites a integrar (insumo da fase)

Chefs/marcas individuais por país: Paola Carosella (paolacarosella.com.br, BR/AR), Lorena
Salinas/Cravings Journal (cravingsjournal.com, PE), Erica Dinho/My Colombian Recipes
(mycolombianrecipes.com, CO), Pilar Hernandez/Chilean Food & Garden (chileanfoodandgarden.com,
CL), Samin Nosrat (ciaosamin.com, US/IR), David Leite/Leite's Culinaria (leitesculinaria.com,
PT/US), Marion Grasby/Marion's Kitchen (marionskitchen.com, AU/TH), The Modern Proper
(themodernproper.com, US), Hannah Sunderani/Two Spoons (twospoons.ca, CA), Shihoko Ura/Chopstick
Chronicles (chopstickchronicles.com, JP), Hyosun/Korean Bapsang (koreanbapsang.com, KR), Andrea
Nguyen/Viet World Kitchen (vietworldkitchen.com, VN), Daddy Lau/Made With Lau (madewithlau.com,
CN), Mandy/Souped Up Recipes (soupeduprecipes.com, CN), Benedetta Rossi/Fatto in Casa
(fattoincasadabenedetta.it, IT), Sonia Peronaci (soniaperonaci.it, IT), Argiro Barbarigou
(argiro.gr, GR), Alia Laskar/Cooking with Alia (cookingwithalia.com, MA), Archana Doshi/Archana's
Kitchen (archanaskitchen.com, IN), Yosra Hamden/Zaatar & Zaytoun (zaatarandzaytoun.com, LB), Yeji's
Kitchen Stories (yejiskitchenstories.com, KR), Imma Allen/African Bites (africanbites.com, NG/US),
Chef Tariq (cheftariq.com, ME), Clotilde Dusoulier/Chocolate & Zucchini (cnz.to, FR), Karlos
Arguiñano/Hogarmania (hogarmania.com, ES), Rick Stein (rickstein.com, UK), Raymond Blanc
(raymondblanc.com, FR), Sally McKenney/Sally's Baking (sallysbakingaddiction.com, US), Dana
Shulman/Minimalist Baker (minimalistbaker.com, US), Lindsay Ostrom/Pinch of Yum (pinchofyum.com,
US), Jeanine Donofrio/Love and Lemons (loveandlemons.com, US), Lisa Bryan/Downshiftology
(downshiftology.com, US), Ali Martin/Gimme Some Oven (gimmesomeoven.com, US), Joy Wilson/Joy the
Baker (joythebaker.com, US).

Marcas/editoriais: Great British Chefs (greatbritishchefs.com, UK), Great Italian Chefs
(greatitalianchefs.com, IT), Great Spanish Chefs (greatspanishchefs.com, ES), Great Polish Chefs
(greatpolishchefs.com, PL), GialloZafferano (giallozafferano.it, IT), King Arthur Baking
(kingarthurbaking.com, US), Saveur (saveur.com, US), The Kitchn (thekitchn.com, US).

Coquetéis: Liquor.com (liquor.com, US), Punch (punchdrink.com, US), Difford's Guide
(diffordsguide.com, UK).

Requer navegador (Playwright): Ranveer Brar (ranveerbrar.com, IN), Ken Hom (kenhom.com, CN/UK),
Chung-Ah Rhee/Damn Delicious (damndelicious.net, US), Food52 (food52.com, US), Mely
Martínez/Mexico in My Kitchen (mexicoinmykitchen.com, MX).

Bloqueado na verificação, acessível via Python: BBC Good Food (bbcgoodfood.com, UK), Bon Appétit
(bonappetit.com, US), Epicurious (epicurious.com, US), Food & Wine (foodandwine.com, US), Martha
Stewart (marthastewart.com, US), Delish (delish.com, US), The Spruce Eats (thespruceeats.com, US).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A maioria dos ~58 sites da Lista 2 (meta: ≥ 80%, ou seja ≥ ~46 sites) é integrada
  ao catálogo com ≥ 10 receitas válidas e vivas cada.
- **SC-002**: O número de países representados no catálogo aumenta (novos países: Peru, Colômbia,
  Chile, Canadá, Marrocos, Líbano, Arábia Saudita, entre outros) — meta de ≥ 10 países novos.
- **SC-003**: Nenhum chef/site da Lista 1 é perdido durante a expansão (os 30 existentes
  continuam no catálogo após a integração).
- **SC-004**: 100% dos registros adicionados estão no contrato {chef, site, titulo, url} e 0
  duplicatas por URL normalizada no catálogo final.
- **SC-005**: Para cada site não integrado, há um motivo documentado (morto, Cloudflare sem
  wayback viável, sem receitas detectáveis) — nenhuma omissão silenciosa.

## Assumptions

Decisões confirmadas em `/speckit-clarify` (Sessão 2026-06-08) e premissas de implementação:

- **Escopo/meta**: tentar TODOS os ~58 sites, em lotes; um site conta como "integrado" se trouxer
  ≥ 10 receitas válidas e vivas. Sites com 0 são documentados, não tratados como falha da fase.
- **Marcas/editoriais**: o nome da marca ocupa o campo `chef` (consistente com "The Woks of Life",
  já existente). O sorteio em duas etapas (chef → receita) trata a marca como um "chef".
- **Coquetéis**: incluídos no mesmo catálogo/contrato (o produto é "o que você vai preparar").
- **Sites "bloqueado na verificação, acessível via Python"**: coletados por HTTP normal (com
  User-Agent de navegador quando preciso); `url_viva` já considera 403/429 como vivo; wayback só
  se o site for totalmente inacessível.
- **Método de implementação**: lotes de ~8–10 sites com sub-agentes em paralelo (1 por site),
  como nas Fases 2/3 — cada um sonda a técnica, escreve o adaptador e valida `coletar(10)`.
- **Teto de coleta por site**: usar `--limite` adequado por técnica (sitemap escala; crawl
  plateia); a definição fina do teto fica para a fase de implementação/curadoria.
- **Dependências**: reutiliza scrapers/base.py (5 técnicas), orquestrador.py (modo `--site`,
  dedup, verificação de URL viva, gravação atômica) e Playwright/Chromium já instalados.
- **Fora de escopo**: frontend, sorteio, contrato de dados, automação de CI, remoção da Lista 1.
