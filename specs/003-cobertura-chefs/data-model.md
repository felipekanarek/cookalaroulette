# Data Model — Fase 3 — Ampliação de cobertura

**Date**: 2026-06-05 · **Feature**: 003-cobertura-chefs

A Fase 3 **não muda o modelo de dados** — apenas amplia o volume e a diversidade. O
contrato e as entidades são os mesmos da Fase 2; o que cresce é o número de adaptadores e
de registros consolidados.

## Entidade: Registro de receita (inalterado)

Contrato `{chef, site, titulo, url}`, schema em
`specs/001-fundacao-sorteio/contracts/receitas.schema.json`. `titulo` = nome da receita
(rótulo), nunca conteúdo (Princípio III). `url` verificada como viva (2xx, ou 401/403/429 =
existe mas restringe bots) antes de gravar.

## Entidade (interna): Adaptador de site

Mesma interface da Fase 2 (`CHEF`, `SITE`, `TECNICAS`, `coletar(limite)`). Novidade da
Fase 3: a técnica pode ser **listagem** (sites sem sitemap) ou **sitemap-via-navegador**
(sites bloqueados), além de sitemap simples. O catálogo dos 38 está em
[contracts/chefs-catalog.md](./contracts/chefs-catalog.md).

## Helpers compartilhados (novos em base.py)

| Helper | Entrada | Saída |
|--------|---------|-------|
| `coletar_por_sitemap` (Fase 2) | base_url, chef, site, filtro, limite, sub_filtro | registros |
| `coletar_por_sitemap_browser` (novo) | idem, via Playwright (corpo bruto, recursa índice) | registros |
| `coletar_por_listagem` (novo) | urls_listagem, chef, site, filtro, limite, usar_browser | registros |

Todos retornam registros já no contrato; o orquestrador faz o resto.

## Pipeline do orquestrador (inalterado + 1 reforço)

1. Para cada adaptador: `coletar(limite)` com **timeout por adaptador** (novo — evita um
   site preso travar a rodada).
2. Bloqueio mesmo após fallback → `bloqueado-pulado`; erro/timeout → reportado; segue (FR-008).
3. Consolidar → descartar inválidos → **deduplicar por URL** (FR-007) → **verificar URLs
   vivas** (FR-007) → **gravar atômico**, **nunca vazio** (FR-010) → **relatório** (FR-012).

## Relatório de cobertura (FR-012)

Por site: técnica usada, coletadas, duplicatas removidas, URLs descartadas, status
(`ok` / `bloqueado-pulado` / `sem-receitas` / `erro` / `timeout`). Agregado: total de
chefs e países representados no `data/receitas.json` final (evidencia SC-001).

## Sem estado persistente além do contrato

Nenhum cache, histórico ou conteúdo de receita é guardado. Saída única: `data/receitas.json`.
