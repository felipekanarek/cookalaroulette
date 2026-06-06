---
description: "Task list — Fase 2 — Scraper (indexação automatizada de receitas)"
---

# Tasks: Fase 2 — Scraper (indexação automatizada de receitas)

**Input**: Design documents from `specs/002-scraper-receitas/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/adapter-contract.md, quickstart.md

**Tests**: Inclui um teste automatizado (Python + `assert`) para os helpers puros do
orquestrador (validação, dedup, normalização, filtro de URL), explicitamente solicitado.
Os adaptadores dependem de rede e são validados manualmente via quickstart.

**Organization**: Tarefas agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: pode rodar em paralelo (arquivos diferentes, sem dependências pendentes)
- **[Story]**: a qual user story a tarefa pertence (US1, US2, US3)
- Caminhos relativos à raiz `/Users/infoprice/cookAlaRoulette/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependências e esqueleto do pacote Python (sem tocar o frontend).

- [X] T001 Criar `requirements.txt` na raiz com `beautifulsoup4`, `lxml`, `requests`, `playwright`
- [X] T002 [P] Criar `scrapers/__init__.py` para tornar `scrapers/` um pacote Python
- [X] T003 Preparar o ambiente conforme o quickstart: `python3 -m venv .venv`, `pip install -r requirements.txt`, `playwright install chromium`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: O núcleo compartilhado por todos os adaptadores e pelo orquestrador.

**⚠️ CRITICAL**: Nenhuma user story começa antes desta fase.

- [X] T004 Implementar `scrapers/base.py`: GET educado (User-Agent realista, timeout, retry/backoff em 5xx/timeout), descoberta+parse de sitemap (ler `robots.txt` → `Sitemap:`, fallback `/sitemap.xml`, seguir índices aninhados, extrair `<loc>`), construtor+validador de registro `{chef, site, titulo, url}` (campos não-vazios, `url` casa `^https?://`), executor "técnica-em-ordem", e a exceção `BloqueioError`

**Checkpoint**: helpers de coleta e validação prontos — adaptadores e orquestrador podem ser construídos.

---

## Phase 3: User Story 1 - Gerar uma curadoria válida automaticamente (Priority: P1) 🎯 MVP

**Goal**: Rodar o orquestrador com um adaptador e gerar um `data/receitas.json` válido que o frontend consome.

**Independent Test**: `python orquestrador.py --limite 20` com apenas o adaptador da RecipeTin Eats registrado → `data/receitas.json` é um array conforme o contrato; abrir o frontend e sortear funciona.

### Implementation for User Story 1

- [X] T005 [US1] Implementar `scrapers/recipetineats.py` (`CHEF="Nagi Maehashi"`, `SITE="recipetineats.com"`, `TECNICAS=["sitemap"]`): `coletar(limite)` via sitemap, com filtro de URL de receita individual, retornando registros do contrato
- [X] T006 [US1] Implementar o núcleo de `orquestrador.py`: registry de adaptadores, ler `--limite` (padrão 50), chamar `coletar(limite)` de cada adaptador, consolidar, **validar** cada registro contra o contrato (descartar inválidos), e **gravar** `data/receitas.json` de forma atômica (arquivo temporário + `os.replace`); imprimir contagem por site

**Checkpoint**: pipeline coleta→valida→grava funcionando com 1 adaptador — MVP entregável.

---

## Phase 4: User Story 2 - Cobrir múltiplos sites com a técnica certa (Priority: P2)

**Goal**: Adaptadores para os demais sites estáticos/sitemap, todos no mesmo contrato.

**Independent Test**: Rodar o orquestrador com os adaptadores de Panelinha, Jamie Oliver, RecipeTin Eats e Serious Eats → `data/receitas.json` contém receitas de múltiplos Chefs/sites, todas no formato `{chef, site, titulo, url}`.

### Implementation for User Story 2

- [ ] T007 [P] [US2] Implementar `scrapers/panelinha.py` (Rita Lobo; sitemap/BS4; filtro de URL contendo `/receita/`)
- [X] T008 [P] [US2] Implementar `scrapers/jamieoliver.py` (Jamie Oliver; sitemap/BS4; filtro `/recipes/<categoria>/<slug>/`, excluindo raiz/categorias)
- [ ] T009 [P] [US2] Implementar `scrapers/seriouseats.py` (Kenji López-Alt; sitemap/BS4; filtro de URL de receita)
- [X] T010 [US2] Registrar `panelinha`, `jamieoliver` e `seriouseats` na lista de adaptadores do `orquestrador.py`

**Checkpoint**: coleta cobre 4 sites com sitemap/BS4, todos no mesmo contrato.

---

## Phase 5: User Story 3 - Coleta robusta diante de bloqueios e erros (Priority: P3)

**Goal**: Site bloqueado não derruba a coleta; saída sem duplicatas e sem URLs mortas; relatório claro.

**Independent Test**: Rodar incluindo a Maangchi (bloqueada) e verificar que (a) os demais sites coletam normalmente, (b) a Maangchi é reportada sem abortar, (c) `data/receitas.json` não tem duplicatas nem URLs que não resolvem.

### Implementation for User Story 3

- [X] T011 [P] [US3] Implementar `scrapers/maangchi.py` (Maangchi; tenta `requests` e, em bloqueio 403, **fallback Playwright uma vez**; se persistir, levanta `BloqueioError`) e registrá-lo no `orquestrador.py`
- [X] T012 [US3] No `orquestrador.py`: tratar `BloqueioError` de um adaptador → marcar o site como `bloqueado-pulado` e **continuar** os demais (FR-009)
- [X] T013 [US3] No `orquestrador.py`: `normalizar_url` (minúsculas em esquema/host, remover fragmento, normalizar barra final) e **deduplicar** por URL normalizada (FR-007)
- [X] T014 [US3] No `orquestrador.py`: **verificar URLs vivas** — HEAD (fallback GET em 405), seguir redirects, manter só 2xx, descartar mortas; usar um pequeno pool de threads (FR-015)
- [X] T015 [US3] No `orquestrador.py`: **relatório de execução** por site (técnica usada, coletadas, duplicatas removidas, URLs mortas descartadas, status) ao final (FR-010)
- [X] T016 [P] [US3] Implementar `tests/test_orquestrador.py` (Python + `assert`, sem rede): testar `validar_registro`, `normalizar_url`, deduplicação e o filtro de URL de receita

**Checkpoint**: coleta robusta, saída limpa e observável.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação fim-a-fim e conformidade.

- [X] T017 Rodar `python orquestrador.py` nos 5 sites e validar os critérios: ≥30 receitas de ≥3 sites (SC-001), 100% conformes (SC-002), 0 duplicatas (SC-003), ≥90% das URLs vivas (SC-004), Maangchi bloqueada não zera os demais (SC-005)
- [X] T018 [P] Servir o frontend (`python3 -m http.server 8000`) e confirmar que sorteia sobre os dados gerados **sem nenhuma alteração no frontend** (Princípio IV / SC-006)
- [X] T019 [P] Atualizar `scrapers/README.md` para refletir os adaptadores implementados (mantendo a referência ao contrato)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sem dependências
- **Foundational (Phase 2)**: depende do Setup — `base.py` BLOQUEIA todas as user stories
- **US1 (Phase 3)**: precisa de `base.py` (T004) — entrega o pipeline (MVP)
- **US2 (Phase 4)**: precisa de `base.py` + orquestrador (T006); os adaptadores T007–T009 são paralelos entre si
- **US3 (Phase 5)**: precisa do orquestrador (T006); T012–T015 editam `orquestrador.py` (sequenciais entre si); T011 e T016 são arquivos próprios ([P])
- **Polish (Phase 6)**: depende das user stories desejadas

### Within Each User Story

- US1: T005 (adaptador) → T006 (orquestrador grava/valida)
- US2: T007 ∥ T008 ∥ T009 (adaptadores) → T010 (registrar)
- US3: T011 ∥ T016 (arquivos próprios); T012 → T013 → T014 → T015 (todos em `orquestrador.py`, sequenciais)

### Parallel Opportunities

- Setup: T002 em paralelo ao restante
- US2: os 3 adaptadores (T007, T008, T009) em paralelo — arquivos diferentes
- US3: `maangchi.py` (T011) e o teste (T016) em paralelo às edições do orquestrador
- Polish: T018 e T019 em paralelo

---

## Parallel Example: User Story 2

```bash
# Adaptadores independentes (arquivos diferentes), em paralelo:
Task: "T007 scrapers/panelinha.py"
Task: "T008 scrapers/jamieoliver.py"
Task: "T009 scrapers/seriouseats.py"
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Phase 1: Setup (requirements + ambiente)
2. Phase 2: Foundational (`base.py` — CRÍTICO)
3. Phase 3: US1 — 1 adaptador (RecipeTin Eats) + orquestrador grava `receitas.json` válido
4. **PARAR e VALIDAR**: rodar, abrir o frontend, ver o sorteio sobre dados coletados
5. É o MVP da Fase 2

### Incremental Delivery

1. Setup + Foundational → base pronta
2. US1 → pipeline ponta a ponta (1 site) → MVP
3. US2 → cobre 4 sites com sitemap/BS4
4. US3 → robustez (Maangchi/bloqueio, dedup, URLs vivas, relatório)
5. Polish → validação dos critérios + frontend intocado

---

## Notes

- [P] = arquivos diferentes, sem dependências pendentes
- Edições no mesmo arquivo (`orquestrador.py`: T012–T015) são sequenciais
- Sem banco, sem framework além das ferramentas de coleta autorizadas; validação em Python puro
- Coletar APENAS `{chef, site, titulo, url}` — nunca conteúdo (Princípio III)
- O orquestrador é o ÚNICO que escreve `data/receitas.json`; o frontend não é tocado (Princípio IV)
- Projeto sem git: não há tarefas de branch/commit
