# Implementation Plan: Expansão de Cobertura (Lista 2)

**Branch**: `005-expansao-cobertura` | **Date**: 2026-06-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-expansao-cobertura/spec.md`

## Summary

Adicionar ~58 novos sites de chefs/marcas (Lista 2) ao scraper, ampliando países e categorias
(inclui coquetéis e editoriais), no contrato de dados existente `{chef, site, titulo, url}`.
Abordagem técnica: um adaptador Python por site em `scrapers/<site>.py` (Princípios V e VIII),
reaproveitando integralmente a infraestrutura madura — `scrapers/base.py` (5 técnicas: sitemap,
sitemap-via-navegador, crawl BFS, listagem, wayback) e `orquestrador.py` (modo cirúrgico `--site`
com mesclagem, dedup por URL, verificação de URL viva tratando 403/429 como vivo, gravação
atômica). Implementação em lotes paralelos (sub-agentes, 1 por site) como nas Fases 2/3; cada
adaptador sonda a técnica mais simples que funciona, valida `coletar(10)` isolado, é registrado
no orquestrador e integrado via `--site` preservando a Lista 1. Nenhuma mudança no frontend, no
sorteio ou no contrato (Princípio IV).

## Technical Context

**Language/Version**: Python 3.9 (compatível com o já instalado)  
**Primary Dependencies**: requests, beautifulsoup4, lxml, playwright (Chromium) — já em requirements.txt  
**Storage**: `data/receitas.json` (JSON único; sem banco de dados)  
**Testing**: validação por adaptador via `coletar(10)` isolado; `tests/test_scrapers.py` e `tests/test_orquestrador.py` (helpers puros); node test do sorteio não se aplica (frontend intocado)  
**Target Platform**: execução offline/sob demanda no terminal do mantenedor (macOS); saída servida estática via GitHub Pages  
**Project Type**: scraper Python (componente isolado do frontend)  
**Performance Goals**: não é tempo-real; coleta educada (espera entre requisições em base.get). Teto por site via `--limite`, ajustado por técnica (sitemap escala; crawl plateia)  
**Constraints**: coleta APENAS localização (URL), nunca conteúdo (Princípio III); sites Cloudflare via wayback sem evasão; falha isolada de um adaptador não derruba os demais (FR-014)  
**Scale/Scope**: +~58 adaptadores; catálogo já em ~38k receitas / 30 chefs → meta ≥46 sites novos integrados, ≥10 países novos. Atenção ao tamanho do `receitas.json` (hoje ~0,8 MB gzip) — payload do frontend cresce com o catálogo.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Conformidade |
|-----------|--------------|
| I. Minimalismo Radical (UX) | ✅ N/A — não toca a tela; nenhum elemento de UI adicionado. |
| II. Zero Fricção | ✅ N/A — fluxo de uso inalterado. |
| III. Redirecionar, Nunca Hospedar | ✅ Adaptadores coletam só a URL (localização), nunca o conteúdo. |
| IV. Separação Estrita Scraper ↔ Frontend | ✅ Mexe só em `scrapers/*` + `orquestrador.py` → `receitas.json`; frontend intocado. |
| V. Contrato Único dos Adaptadores | ✅ Todos retornam `{chef, site, titulo, url}`; sem vazar formato do site. |
| VI. Fundamentos sem Frameworks | ✅ Só ferramentas de coleta permitidas (bs4, Playwright, sitemap). |
| VII. Aprendizado em Primeiro Lugar | ✅ Cada adaptador sonda e escolhe a técnica mais simples (sem atalho opaco). |
| VIII. Escala por Adição | ✅ Adicionar site = um arquivo + um registro; sem mudança de arquitetura/contrato. |

**Estratégia de coleta (ordem obrigatória da constituição)** respeitada: sitemap → BeautifulSoup
(listagem/crawl HTML) → Playwright; wayback como recurso legítimo para Cloudflare. **Resultado do
gate: PASS** — nenhuma violação; seção de Complexity Tracking não necessária.

## Project Structure

### Documentation (this feature)

```text
specs/005-expansao-cobertura/
├── plan.md              # Este arquivo (/speckit.plan)
├── research.md          # Fase 0 — decisões de técnica por site/categoria
├── data-model.md        # Fase 1 — entidades (Adaptador, Registro, Catálogo, Relatório)
├── quickstart.md        # Fase 1 — como criar/validar/integrar um adaptador
├── contracts/
│   └── adaptador.md     # Fase 1 — contrato da interface de adaptador + registro
├── checklists/
│   └── requirements.md  # Checklist de qualidade da spec (já criado)
└── tasks.md             # Fase 2 (/speckit.tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
scrapers/
├── base.py                 # (existente) 5 técnicas de coleta — reutilizado, sem alteração esperada
├── <novosite>.py           # (NOVO) um por site da Lista 2 — CHEF/SITE/TECNICAS/coletar(limite)
└── ... (adaptadores da Lista 1, intocados)

orquestrador.py             # (existente) registra novos adaptadores (import + ADAPTADORES); modo --site
data/receitas.json          # (saída) catálogo mesclado — Lista 1 + Lista 2
tests/
├── test_scrapers.py        # (existente) helpers de coleta
└── test_orquestrador.py    # (existente) helpers do orquestrador

# Frontend (index.html, app.js, style.css, sorteio.js): INTOCADO (Princípio IV)
```

**Structure Decision**: scraper Python já estabelecido (Fases 2–4). Esta fase apenas **adiciona
arquivos** `scrapers/<site>.py` e os registra no `orquestrador.py`. `base.py` e `orquestrador.py`
só recebem mudança se um site novo exigir um helper/ajuste genérico (ex.: nova variação de
listagem) — preferir reutilizar o que existe.

## Complexity Tracking

> Não aplicável — Constitution Check passou sem violações.
