---
description: "Task list — Fase 3 — Ampliação de cobertura (38 chefs)"
---

# Tasks: Fase 3 — Integração e ampliação de cobertura

**Input**: Design documents from `specs/003-cobertura-chefs/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chefs-catalog.md, quickstart.md

**Tests**: Inclui teste automatizado (`tests/test_scrapers.py`) para os helpers puros novos
(extração/normalização de links, filtros), explicitamente pedido. Adaptadores dependem de
rede → validados por execução + relatório.

**Organization**: Por user story (P1 diversidade via sitemap, P2 sem-sitemap, P3 bloqueados),
entregue em **lotes**. Cada adaptador é um arquivo próprio (`scrapers/<site>.py`) — [P] entre si.

> ⚠️ **Cada adaptador é bespoke**: a "técnica inicial" do [chefs-catalog.md](./contracts/chefs-catalog.md)
> é um palpite; ao implementar, **sondar `robots.txt`/sitemap e testar requests vs. bloqueio**,
> e mover o chef de lote se necessário (ex.: um "sitemap" que dá 403 vira Lote 2). Definir o
> filtro de URL de receita por site e respeitar o teto (FR-014). Nunca coletar conteúdo (III).

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [X] T001 Confirmar ambiente (deps da Fase 2 já instaladas: requests, beautifulsoup4, lxml, playwright + Chromium). Sem novas dependências.

---

## Phase 2: Foundational (Blocking Prerequisites)

**⚠️ CRITICAL**: os helpers compartilhados são pré-requisito de todos os lotes.

- [X] T002 Implementar `coletar_por_sitemap_browser()` em `scrapers/base.py`: via Playwright, busca o sitemap pelo **corpo bruto** (`resp.text()`, não o DOM), recursa em índices, aplica filtro de URL e `sub_filtro` — generaliza a lógica que funcionou na Maangchi
- [X] T003 Implementar `coletar_por_listagem()` em `scrapers/base.py`: busca página(s) de listagem com requests+BS4 (Playwright se `usar_browser=True`/JS), extrai `<a href>`, normaliza para absoluto, filtra com `url_e_receita`, título do texto do link ou slug
- [ ] T004 Adicionar **timeout por adaptador** no `orquestrador.py` (um site lento/preso não trava a rodada de 38; timeout → status reportado, segue)
- [X] T005 [P] Implementar `tests/test_scrapers.py` (Python + `assert`, sem rede): testar extração/normalização de links de listagem e os filtros de URL dos novos adaptadores

**Checkpoint**: helpers de sitemap-browser e listagem prontos — lotes podem começar.

---

## Phase 3: User Story 1 - Diversidade via sitemap (Priority: P1) 🎯 — Lote 1

**Goal**: cobrir a maioria dos chefs (blogs WordPress/Yoast) via `coletar_por_sitemap`.

**Independent Test**: após este lote + registro, rodar o orquestrador e ver receitas de muitos países no `data/receitas.json`, todas levando a páginas reais.

> Cada task: criar `scrapers/<site>.py` (CHEF/SITE/TECNICAS=["sitemap"], `coletar` via `base.coletar_por_sitemap` com sub-filtro de posts/stoplist conforme o caso + filtro de URL de receita do site). Sondar a estrutura antes.

- [X] T006 [P] [US1] `scrapers/belagil.py` — Bela Gil (belagil.com, 🇧🇷)
- [X] T007 [P] [US1] `scrapers/laylita.py` — Layla Pujol (laylita.com, 🇪🇨)
- [X] T008 [P] [US1] `scrapers/ceciliatupac.py` — Cecilia Tupac (ceciliatupac.com, 🇵🇪)
- [X] T009 [P] [US1] `scrapers/paulinacocina.py` — Paulina Cocina (paulinacocina.net, 🇦🇷)
- [X] T010 [P] [US1] `scrapers/patijinich.py` — Pati Jinich (patijinich.com, 🇲🇽)
- [X] T011 [P] [US1] `scrapers/nigella.py` — Nigella Lawson (nigella.com, 🇬🇧)
- [X] T012 [P] [US1] `scrapers/ottolenghi.py` — Yotam Ottolenghi (ottolenghi.co.uk, 🇬🇧)
- [X] T013 [P] [US1] `scrapers/donalskehan.py` — Donal Skehan (donalskehan.com, 🇮🇪)
- [X] T014 [P] [US1] `scrapers/smittenkitchen.py` — Deb Perelman (smittenkitchen.com, 🇺🇸)
- [ ] T015 [P] [US1] `scrapers/halfbakedharvest.py` — Tieghan Gerard (halfbakedharvest.com, 🇺🇸)
- [ ] T016 [P] [US1] `scrapers/joshuaweissman.py` — Joshua Weissman (joshuaweissman.com, 🇺🇸)
- [X] T017 [P] [US1] `scrapers/akispetretzikis.py` — Akis Petretzikis (akispetretzikis.com, 🇬🇷)
- [X] T018 [P] [US1] `scrapers/davidlebovitz.py` — David Lebovitz (davidlebovitz.com, 🇫🇷)
- [X] T019 [P] [US1] `scrapers/vincenzosplate.py` — Vincenzo's Plate (vincenzosplate.com, 🇮🇹)
- [X] T020 [P] [US1] `scrapers/misya.py` — Flavia Imperatore (misya.info, 🇮🇹)
- [X] T021 [P] [US1] `scrapers/thespanishchef.py` — Omar Allibhoy (thespanishchef.com, 🇪🇸)
- [X] T022 [P] [US1] `scrapers/kwestiasmaku.py` — Joanna / Kwestia Smaku (kwestiasmaku.com, 🇵🇱)
- [ ] T023 [P] [US1] `scrapers/mojewypieki.py` — Dorota Świątkowska (mojewypieki.com, 🇵🇱)
- [X] T024 [P] [US1] `scrapers/natashaskitchen.py` — Natasha Kravchuk (natashaskitchen.com, 🇺🇦)
- [X] T025 [P] [US1] `scrapers/northwildkitchen.py` — Nevada Berg (northwildkitchen.com, 🇳🇴)
- [X] T026 [P] [US1] `scrapers/trinehahnemann.py` — Trine Hahnemann (trinehahnemann.com, 🇩🇰)
- [X] T027 [P] [US1] `scrapers/callmecupcake.py` — Linda Lomelino (callmecupcake.se, 🇸🇪)
- [X] T028 [P] [US1] `scrapers/kitchenbutterfly.py` — Ozoz Sokoh (kitchenbutterfly.com, 🇳🇬)
- [X] T029 [P] [US1] `scrapers/simplydelicious.py` — Alida Ryder (simply-delicious-food.com, 🇿🇦)
- [X] T030 [P] [US1] `scrapers/justonecookbook.py` — Namiko Chen (justonecookbook.com, 🇯🇵)
- [X] T031 [P] [US1] `scrapers/thewoksoflife.py` — The Woks of Life (thewoksoflife.com, 🇨🇳)
- [X] T032 [P] [US1] `scrapers/hotthaikitchen.py` — Pailin Chongchitnant (hot-thai-kitchen.com, 🇹🇭)
- [X] T033 [P] [US1] `scrapers/adamliaw.py` — Adam Liaw (adamliaw.com, 🇦🇺)
- [ ] T034 [US1] Registrar todos os adaptadores do Lote 1 na lista `ADAPTADORES` do `orquestrador.py`

**Checkpoint**: ampla diversidade já coletável; SC-001 provavelmente atingido só com este lote.

---

## Phase 4: User Story 2 - Sites sem sitemap (Priority: P2) — Lote 3

**Goal**: cobrir chefs cujos sites não expõem sitemap, via `coletar_por_listagem`.

**Independent Test**: rodar um adaptador de site sem sitemap e ver receitas reais no contrato.

- [X] T035 [P] [US2] Reescrever `scrapers/panelinha.py` — Rita Lobo (panelinha.com.br, 🇧🇷): coleta via listagem (`coletar_por_listagem`), filtro `/receita/<slug>` (sem sitemap — pendência da Fase 2)
- [ ] T036 [P] [US2] `scrapers/barefootcontessa.py` — Ina Garten (barefootcontessa.com, 🇺🇸): sondar; listagem se não houver sitemap
- [ ] T037 [P] [US2] `scrapers/zoesghana.py` — Zoe Adjonyoh (zoesghana.com, 🇬🇭): sondar; listagem se não houver sitemap
- [X] T038 [P] [US2] `scrapers/danangcuisine.py` — Helen Le (danangcuisine.com, 🇻🇳): sondar; listagem se não houver sitemap
- [ ] T039 [US2] Registrar os adaptadores do Lote 3 na lista `ADAPTADORES` do `orquestrador.py`

**Checkpoint**: ≥1 site sem sitemap contribui (SC-004, parte 1).

---

## Phase 5: User Story 3 - Sites bloqueados (Priority: P3) — Lote 2

**Goal**: recuperar chefs cujos sites bloqueiam bots, via `coletar_por_sitemap_browser`.

**Independent Test**: rodar um adaptador de site bloqueado e ver o fallback de navegador recuperar receitas; se persistir, reportado e pulado.

- [X] T040 [P] [US3] Completar `scrapers/seriouseats.py` — Kenji López-Alt (seriouseats.com, 🇺🇸): fallback `coletar_por_sitemap_browser` (sub-sitemaps dão 403 ao requests); ajustar filtro de URL de receita (pendência da Fase 2)
- [ ] T041 [P] [US3] `scrapers/gordonramsay.py` — Gordon Ramsay (gordonramsay.com, 🇬🇧): sondar; `coletar_por_sitemap_browser` se bloquear
- [X] T042 [P] [US3] `scrapers/sanjeevkapoor.py` — Sanjeev Kapoor (sanjeevkapoor.com, 🇮🇳): sondar; sitemap ou fallback browser
- [ ] T043 [US3] Registrar os adaptadores do Lote 2 na lista `ADAPTADORES` do `orquestrador.py`

**Checkpoint**: ≥1 site antes bloqueado contribui (SC-004, parte 2).

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T044 Rodar `python orquestrador.py` (todos os adaptadores) e validar: **≥25 chefs / ≥18 países** (SC-001), 100% conformes (SC-002), 0 duplicatas (SC-003), URLs vivas (SC-003), nenhum site derruba os demais e arquivo nunca vazio (SC-005)
- [X] T045 [P] Servir o frontend e confirmar que sorteia sobre a curadoria ampliada **sem nenhuma alteração no frontend** (SC-006 / Princípio IV)
- [X] T046 [P] Atualizar `contracts/chefs-catalog.md` (status real por chef) e `scrapers/README.md` (técnica final de cada adaptador)
- [X] T047 [P] Conferir que a estratégia de re-indexação (manual + exemplo de cron) está documentada no `quickstart.md` (SC-007)

---

## Dependencies & Execution Order

- **Setup (T001)** → **Foundational (T002–T005)**: os 2 helpers + timeout + teste BLOQUEIAM os lotes.
- **Lotes (US1/US2/US3)**: dependem dos helpers. Adaptadores são [P] entre si (arquivos próprios). As tasks de **registro** (T034, T039, T043) editam `orquestrador.py` → sequenciais entre si.
- US1 (Lote 1) sozinho já tende a cumprir SC-001; US2 e US3 cumprem o SC-004 (sem-sitemap + bloqueado).
- **Polish (T044–T047)**: depois dos lotes desejados.

### Nota sobre técnica "a confirmar"
Ao implementar cada adaptador, sondar primeiro (`robots.txt`, `/sitemap.xml`, requests vs. 403).
Se o palpite do catálogo estiver errado, trocar o helper usado (sitemap ↔ sitemap-browser ↔
listagem) — o chef pode mudar de lote. Isso é esperado (scraping é bespoke; Princípio VII).

---

## Parallel Example: Lote 1 (US1)

```bash
# Adaptadores de sitemap são independentes (arquivos diferentes) — em paralelo:
Task: "T006 scrapers/belagil.py"
Task: "T014 scrapers/smittenkitchen.py"
Task: "T030 scrapers/justonecookbook.py"
# ... etc. Depois T034 registra todos de uma vez.
```

---

## Implementation Strategy

### Incremental por lote (recomendado)

1. Setup + Foundational (helpers) — pré-requisito.
2. **Lote 0** (dentro de US2/US3): Panelinha (T035) + Serious Eats (T040) — destravam as 2 técnicas com casos reais.
3. **Lote 1** (US1): adaptadores de sitemap em paralelo → T034 registra → rodar → já deve bater SC-001.
4. **Lote 2/3** (US3/US2): bloqueados e sem-sitemap → registrar → rodar.
5. Polish: validação final + atualizar catálogo/README.

Parar em qualquer lote é um incremento válido (o `receitas.json` só cresce; frontend intocado).

## Notes

- [P] = arquivos diferentes; tasks de registro no `orquestrador.py` são sequenciais.
- Coletar APENAS `{chef, site, titulo, url}` — nunca conteúdo (Princípio III).
- Orquestrador é o único a escrever `data/receitas.json`; nunca sobrescreve com vazio.
- Sem git: sem tarefas de branch/commit.
