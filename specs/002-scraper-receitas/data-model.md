# Data Model — Fase 2 — Scraper

**Date**: 2026-06-05 · **Feature**: 002-scraper-receitas

## Visão geral

A Fase 2 **produz** o mesmo dado que a Fase 1 consome: um array de registros de receita em
`data/receitas.json`. O formato é o **Contrato Único** (Princípio V), idêntico ao da Fase 1.
A Fase 2 acrescenta dois conceitos internos (não persistidos no contrato): o **Adaptador**
e o **Relatório de execução**.

## Entidade: Registro de receita (saída — o contrato)

Idêntico à Fase 1; schema em
`specs/001-fundacao-sorteio/contracts/receitas.schema.json` (fonte única, reusada).

| Campo | Tipo | Obrigatório | Regra |
|-------|------|-------------|-------|
| `chef` | string | sim | Não-vazio. Nome do Chef (definido pelo adaptador). |
| `site` | string | sim | Não-vazio. Domínio de origem. |
| `titulo` | string | sim | Não-vazio. **Nome** da receita (rótulo) — nunca o conteúdo. |
| `url` | string | sim | URL absoluta `http(s)`, **verificada como viva (2xx)** antes de gravar. |

Saída: `data/receitas.json` = array desses objetos, **sem duplicatas de URL**.

## Entidade (interna): Adaptador de site

Não persiste. Cada `scrapers/<site>.py` expõe a mesma interface (ver
[contracts/adapter-contract.md](./contracts/adapter-contract.md)).

| Propriedade | Descrição |
|-------------|-----------|
| `CHEF` / `SITE` | Constantes do adaptador (preenchem os campos `chef`/`site`). |
| ordem de técnicas | Lista declarada: ex. `["sitemap", "bs4", "playwright"]`. |
| `coletar(limite)` | Retorna até `limite` registros válidos `{chef, site, titulo, url}` daquele site. |
| filtro de URL | Predicado que decide se uma URL é de receita individual (por site). |

**Elegibilidade de um registro**: campos obrigatórios não-vazios + `url` `http(s)`. Registros
inválidos são descartados pelo orquestrador antes da consolidação.

## Entidade (interna): Relatório de execução

Não persiste no contrato; é a saída de observabilidade do orquestrador (FR-010).

| Campo por site | Significado |
|----------------|-------------|
| `site` / `chef` | quem foi coletado |
| `tecnica` | técnica que funcionou (sitemap / bs4 / playwright) |
| `coletadas` | nº de registros válidos coletados (após teto) |
| `duplicatas_removidas` | nº removido por URL repetida |
| `urls_mortas_descartadas` | nº removido por não resolver (não-2xx) |
| `status` | `ok` / `bloqueado-pulado` / `sem-receitas` / `erro` |

## Regras do pipeline do orquestrador (FR-003, FR-006, FR-007, FR-012, FR-015)

1. Para cada adaptador registrado: chamar `coletar(limite=TETO)` (padrão ~50). FR-014.
2. Se um adaptador sinalizar bloqueio mesmo após fallback Playwright → marcar
   `bloqueado-pulado` e seguir (FR-009).
3. Consolidar todos os registros; **descartar inválidos** (contrato).
4. **Deduplicar** por URL normalizada (FR-007).
5. **Verificar** cada URL (HEAD/GET → 2xx); descartar mortas (FR-015).
6. **Gravar** `data/receitas.json` de forma atômica (temp + `os.replace`) (FR-012).
7. **Emitir** o relatório por site (FR-010).

## Sem conteúdo persistido (Princípio III)

Nenhum ingrediente, texto de preparo, foto ou vídeo é lido para armazenamento. Apenas
`chef`, `site`, `titulo` (nome) e `url`.
