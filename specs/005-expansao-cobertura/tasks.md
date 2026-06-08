# Tasks: Expansão de Cobertura (Lista 2)

**Feature**: `005-expansao-cobertura` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Cada site = um adaptador `scrapers/<modulo>.py` (cria + valida `coletar(10)`). Tarefas de site são
`[P]` (arquivos independentes → sub-agentes paralelos, 1 por site). As tarefas de **registro +
integração** de cada lote são sequenciais (tocam `orquestrador.py` e `data/receitas.json`).
Validação de aceite por site: `python3 -c "from scrapers import <m>; print(len(<m>.coletar(10)))"` ≥ 1
(meta ≥ 10). Contrato `{chef, site, titulo, url}` — só localização, nunca conteúdo.

## Phase 1: Setup

- [X] T001 Confirmar ambiente: `python3 -m playwright install chromium` (se preciso), backup do catálogo (`cp data/receitas.json /tmp/receitas_pre_lista2.json`) e registrar contagem baseline (`python3 -c "import json;d=json.load(open('data/receitas.json'));print(len(d), len({r['chef'] for r in d}))"`)
- [X] T002 Criar `specs/005-expansao-cobertura/cobertura.md` com tabela de status por site (site | módulo | trilha | status | receitas | motivo) para a prestação de contas (SC-005)

## Phase 2: Foundational

- [X] T003 Revisar `scrapers/base.py` — confirmar que os 5 helpers cobrem as técnicas das trilhas A–D; anotar (sem alterar, salvo gap real) qualquer helper a estender (ex.: scroll/"load more" em listagem JS)

## Phase 3: User Story 1 — Mais chefs e países (Priority: P1)

**Goal**: integrar os sites de coleta padrão (trilhas A/B sitemap/listagem + coquetéis).
**Independent Test**: cada `coletar(10)` retorna receitas reais; após integrar o lote, o catálogo cresce e a Lista 1 é preservada.

### Lote 1 — América Latina / Ibéria

- [X] T004 [P] [US1] `scrapers/paolacarosella.py` — Paola Carosella (paolacarosella.com.br, BR/AR)
- [X] T005 [P] [US1] `scrapers/cravingsjournal.py` — Lorena Salinas (cravingsjournal.com, PE)
- [X] T006 [P] [US1] `scrapers/mycolombianrecipes.py` — Erica Dinho (mycolombianrecipes.com, CO)
- [X] T007 [P] [US1] `scrapers/chileanfoodandgarden.py` — Pilar Hernandez (chileanfoodandgarden.com, CL)
- [X] T008 [P] [US1] `scrapers/leitesculinaria.py` — David Leite (leitesculinaria.com, PT/US)
- [X] T009 [P] [US1] `scrapers/hogarmania.py` — Karlos Arguiñano (hogarmania.com, ES)
- [ ] T010 [US1] Registrar T004–T009 em `orquestrador.py` (import + ADAPTADORES) e integrar: `python3 orquestrador.py --site paolacarosella --site cravingsjournal --site mycolombianrecipes --site chileanfoodandgarden --site leitesculinaria --site hogarmania --limite 1000`; atualizar `cobertura.md`

### Lote 2 — Food blogs EUA

- [ ] T011 [P] [US1] `scrapers/ciaosamin.py` — Samin Nosrat (ciaosamin.com, US/IR)
- [ ] T012 [P] [US1] `scrapers/sallysbaking.py` — Sally McKenney (sallysbakingaddiction.com, US)
- [ ] T013 [P] [US1] `scrapers/minimalistbaker.py` — Dana Shulman (minimalistbaker.com, US)
- [ ] T014 [P] [US1] `scrapers/pinchofyum.py` — Lindsay Ostrom (pinchofyum.com, US)
- [ ] T015 [P] [US1] `scrapers/loveandlemons.py` — Jeanine Donofrio (loveandlemons.com, US)
- [ ] T016 [P] [US1] `scrapers/downshiftology.py` — Lisa Bryan (downshiftology.com, US)
- [ ] T017 [P] [US1] `scrapers/gimmesomeoven.py` — Ali Martin (gimmesomeoven.com, US)
- [ ] T018 [P] [US1] `scrapers/joythebaker.py` — Joy Wilson (joythebaker.com, US)
- [ ] T019 [P] [US1] `scrapers/themodernproper.py` — The Modern Proper (themodernproper.com, US)
- [ ] T020 [US1] Registrar T011–T019 em `orquestrador.py` e integrar via `--site` (limite 1000); atualizar `cobertura.md`

### Lote 3 — Ásia

- [ ] T021 [P] [US1] `scrapers/chopstickchronicles.py` — Shihoko Ura (chopstickchronicles.com, JP)
- [ ] T022 [P] [US1] `scrapers/koreanbapsang.py` — Hyosun (koreanbapsang.com, KR)
- [ ] T023 [P] [US1] `scrapers/vietworldkitchen.py` — Andrea Nguyen (vietworldkitchen.com, VN)
- [ ] T024 [P] [US1] `scrapers/madewithlau.py` — Daddy Lau (madewithlau.com, CN)
- [ ] T025 [P] [US1] `scrapers/soupeduprecipes.py` — Mandy (soupeduprecipes.com, CN)
- [ ] T026 [P] [US1] `scrapers/yejiskitchenstories.py` — Yeji (yejiskitchenstories.com, KR)
- [ ] T027 [P] [US1] `scrapers/archanaskitchen.py` — Archana Doshi (archanaskitchen.com, IN)
- [ ] T028 [US1] Registrar T021–T027 em `orquestrador.py` e integrar via `--site` (limite 1000); atualizar `cobertura.md`

### Lote 4 — Europa / Oriente Médio / Oceania / África

- [ ] T029 [P] [US1] `scrapers/fattoincasadabenedetta.py` — Benedetta Rossi (fattoincasadabenedetta.it, IT)
- [ ] T030 [P] [US1] `scrapers/soniaperonaci.py` — Sonia Peronaci (soniaperonaci.it, IT)
- [ ] T031 [P] [US1] `scrapers/argiro.py` — Argiro Barbarigou (argiro.gr, GR)
- [ ] T032 [P] [US1] `scrapers/cookingwithalia.py` — Alia Laskar (cookingwithalia.com, MA)
- [ ] T033 [P] [US1] `scrapers/zaatarandzaytoun.py` — Yosra Hamden (zaatarandzaytoun.com, LB)
- [ ] T034 [P] [US1] `scrapers/cheftariq.py` — Chef Tariq (cheftariq.com, ME)
- [ ] T035 [P] [US1] `scrapers/chocolateandzucchini.py` — Clotilde Dusoulier (cnz.to, FR)
- [ ] T036 [P] [US1] `scrapers/rickstein.py` — Rick Stein (rickstein.com, UK)
- [ ] T037 [P] [US1] `scrapers/raymondblanc.py` — Raymond Blanc (raymondblanc.com, FR)
- [ ] T038 [P] [US1] `scrapers/marionskitchen.py` — Marion Grasby (marionskitchen.com, AU/TH)
- [ ] T039 [P] [US1] `scrapers/twospoons.py` — Hannah Sunderani (twospoons.ca, CA)
- [ ] T040 [P] [US1] `scrapers/africanbites.py` — Imma Allen (africanbites.com, NG/US)
- [ ] T041 [US1] Registrar T029–T040 em `orquestrador.py` e integrar via `--site` (limite 1000); atualizar `cobertura.md`

### Lote 5 — Editorial / marca + coquetéis

- [ ] T042 [P] [US1] `scrapers/greatbritishchefs.py` — Great British Chefs (greatbritishchefs.com, UK)
- [ ] T043 [P] [US1] `scrapers/greatitalianchefs.py` — Great Italian Chefs (greatitalianchefs.com, IT)
- [ ] T044 [P] [US1] `scrapers/greatspanishchefs.py` — Great Spanish Chefs (greatspanishchefs.com, ES)
- [ ] T045 [P] [US1] `scrapers/greatpolishchefs.py` — Great Polish Chefs (greatpolishchefs.com, PL)
- [ ] T046 [P] [US1] `scrapers/giallozafferano.py` — GialloZafferano (giallozafferano.it, IT)
- [ ] T047 [P] [US1] `scrapers/kingarthurbaking.py` — King Arthur Baking (kingarthurbaking.com, US)
- [ ] T048 [P] [US1] `scrapers/saveur.py` — Saveur (saveur.com, US)
- [ ] T049 [P] [US1] `scrapers/thekitchn.py` — The Kitchn (thekitchn.com, US)
- [ ] T050 [P] [US1] `scrapers/liquor.py` — Liquor.com (liquor.com, US — coquetéis)
- [ ] T051 [P] [US1] `scrapers/punchdrink.py` — Punch (punchdrink.com, US — coquetéis)
- [ ] T052 [P] [US1] `scrapers/diffordsguide.py` — Difford's Guide (diffordsguide.com, UK — coquetéis)
- [ ] T053 [US1] Registrar T042–T052 em `orquestrador.py` e integrar via `--site` (limite 1000); atualizar `cobertura.md`

**Checkpoint US1**: maioria dos ~45 sites integrados; catálogo cresceu; Lista 1 preservada.

## Phase 4: User Story 2 — Sites difíceis (Priority: P2)

**Goal**: integrar sites que exigem navegador (trilha C) ou bloqueiam a verificação (trilha D).
**Independent Test**: site "requer Playwright" coleta via navegador; site bloqueado tem URLs preservadas (403/429 = vivo) ou via wayback.

### Lote 6 — Requer navegador (Playwright)

- [ ] T054 [P] [US2] `scrapers/ranveerbrar.py` — Ranveer Brar (ranveerbrar.com, IN — navegador)
- [ ] T055 [P] [US2] `scrapers/kenhom.py` — Ken Hom (kenhom.com, CN/UK — navegador)
- [ ] T056 [P] [US2] `scrapers/damndelicious.py` — Chung-Ah Rhee (damndelicious.net, US — navegador)
- [ ] T057 [P] [US2] `scrapers/food52.py` — Food52 (food52.com, US — navegador, filtro restritivo + teto moderado)
- [ ] T058 [P] [US2] `scrapers/mexicoinmykitchen.py` — Mely Martínez (mexicoinmykitchen.com, MX — navegador)
- [ ] T059 [US2] Registrar T054–T058 em `orquestrador.py` e integrar via `--site` (limite 1000); atualizar `cobertura.md`

### Lote 7 — Bloqueado na verificação (HTTP via Python; url_viva tolerante / wayback)

- [ ] T060 [P] [US2] `scrapers/bbcgoodfood.py` — BBC Good Food (bbcgoodfood.com, UK)
- [ ] T061 [P] [US2] `scrapers/bonappetit.py` — Bon Appétit (bonappetit.com, US — Condé Nast)
- [ ] T062 [P] [US2] `scrapers/epicurious.py` — Epicurious (epicurious.com, US — Condé Nast)
- [ ] T063 [P] [US2] `scrapers/foodandwine.py` — Food & Wine (foodandwine.com, US — Dotdash)
- [ ] T064 [P] [US2] `scrapers/marthastewart.py` — Martha Stewart (marthastewart.com, US)
- [ ] T065 [P] [US2] `scrapers/delish.py` — Delish (delish.com, US — Hearst)
- [ ] T066 [P] [US2] `scrapers/thespruceeats.py` — The Spruce Eats (thespruceeats.com, US — Dotdash)
- [ ] T067 [US2] Registrar T060–T066 em `orquestrador.py` e integrar via `--site` (limite 1000); atualizar `cobertura.md`

**Checkpoint US2**: sites difíceis tratados pela técnica certa, sem evasão; bloqueados não descartados.

## Phase 5: User Story 3 — Integração e prestação de contas (Priority: P3)

**Goal**: catálogo final consistente + relatório honesto de cobertura.
**Independent Test**: relatório lista cada site (ok/sem-receitas/bloqueado/morto); 0 duplicatas; Lista 1 intacta.

- [ ] T068 [US3] Finalizar `cobertura.md`: para cada site da Lista 2, status final (integrado/contagem ou motivo de não-integração) — SC-005
- [ ] T069 [US3] Verificar invariantes do catálogo: 0 duplicatas por URL normalizada (SC-004), todos os registros válidos, e os 30 chefs da Lista 1 ainda presentes (SC-003) — script de checagem ad-hoc
- [ ] T070 [US3] Conferir métricas de sucesso: nº de sites integrados vs ~58 (SC-001 ≥80%) e nº de países novos (SC-002 ≥10); registrar no `cobertura.md`
- [ ] T071 [US3] Conferir tamanho do `data/receitas.json` (cru + gzip); se o payload do frontend crescer demais, reduzir tetos por site e re-integrar os maiores via `--site`

## Phase 6: Polish & Cross-Cutting

- [ ] T072 Atualizar `README.md` (contagem de chefs/países; nota da Lista 2) e `scrapers/README.md` se existir
- [ ] T073 Atualizar memória do projeto (cookalaroulette-status) com o resultado da Fase 5
- [ ] T074 Commit final + push (`git add data/receitas.json scrapers/ orquestrador.py specs/005-expansao-cobertura`); GitHub Pages republica
- [ ] T075 Merge da branch `005-expansao-cobertura` em `main`

## Dependencies & Execution

- **Setup (T001–T002)** antes de tudo; **Foundational (T003)** antes dos lotes.
- **US1 (P1, T004–T053)**, **US2 (P2, T054–T067)** e **US3 (P3, T068–T071)** em ordem de prioridade.
  US1 e US2 são independentes entre si (sites distintos); US3 depende de US1+US2 terminados.
- Dentro de cada lote: as tarefas de site `[P]` rodam em paralelo (sub-agentes, 1 por site); a
  tarefa de **registro + integração** do lote roda **depois** que os adaptadores do lote passaram
  na validação (toca `orquestrador.py` e `data/receitas.json`, então é sequencial).
- **Sempre uma operação por vez** escrevendo `data/receitas.json` (não rodar dois `--site` simultâneos).

### Exemplo de paralelização (Lote 1)

Disparar 6 sub-agentes em paralelo (T004–T009), cada um sondando a técnica e escrevendo o
adaptador + validando `coletar(10)`. Quando todos passarem, executar T010 (registro + integração).

## Implementation Strategy

- **MVP**: US1 Lote 1 (T004–T010) — primeiro lote integrado já entrega valor (novos países no sorteio).
- **Entrega incremental**: lote a lote; cada `--site` publica o ganho sem re-raspar a Lista 1.
- **Honestidade**: sites mortos/bloqueados sem solução são documentados em `cobertura.md`, não escondidos.

## Resumo

- **Total**: 75 tarefas. **US1 (P1)**: 50 (45 sites + 5 integrações). **US2 (P2)**: 14 (12 sites + 2 integrações). **US3 (P3)**: 4. Setup/Foundational: 3. Polish: 4.
- **Paralelizável**: 57 tarefas de site `[P]` (sub-agentes, 1 por site), em 7 lotes.
- **MVP sugerido**: Lote 1 (T004–T010).
