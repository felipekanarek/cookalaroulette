# Contrato dos Adaptadores — Fase 2

**Feature**: 002-scraper-receitas · **Date**: 2026-06-05

Define a interface que **todo** adaptador (`scrapers/<site>.py`) MUST implementar, para que
o orquestrador os trate de forma uniforme (Princípio V — Contrato Único).

## Saída de dados (o registro)

Cada adaptador produz registros no MESMO formato, validado contra o schema da Fase 1
(fonte única): [`../../001-fundacao-sorteio/contracts/receitas.schema.json`](../../001-fundacao-sorteio/contracts/receitas.schema.json)

```json
{ "chef": "Nagi Maehashi", "site": "recipetineats.com", "titulo": "Butter Chicken", "url": "https://www.recipetineats.com/butter-chicken/" }
```

## Interface do módulo adaptador

Cada `scrapers/<site>.py` MUST expor:

```python
CHEF: str          # ex.: "Nagi Maehashi"  — preenche o campo `chef`
SITE: str          # ex.: "recipetineats.com" — preenche o campo `site`
TECNICAS: list[str]  # ordem a tentar, ex.: ["sitemap", "bs4", "playwright"]

def coletar(limite: int) -> list[dict]:
    """Retorna ATÉ `limite` registros {chef, site, titulo, url} de receitas individuais
    deste site. Não armazena conteúdo. Pode levantar BloqueioError se o site bloquear
    mesmo após o fallback Playwright."""
```

## Regras de conformidade

- **MUST** retornar apenas receitas individuais (aplicar o filtro de URL do site; excluir
  listagens/categorias). — FR-008
- **MUST** respeitar `limite` (teto por site). — FR-014
- **MUST NOT** ler/retornar conteúdo de receita (ingredientes, preparo, mídia). — FR-003/Princípio III
- **MUST** preencher `chef` e `site` com `CHEF`/`SITE`; `titulo` com o nome da receita;
  `url` com a URL absoluta `http(s)` da receita.
- Em bloqueio anti-bot: tentar fallback Playwright **uma vez**; se persistir, sinalizar
  bloqueio (o orquestrador marca `bloqueado-pulado`). — FR-009

## O que o orquestrador faz com a saída (não é responsabilidade do adaptador)

Deduplicação por URL, verificação de URL viva (HEAD/GET → 2xx), validação de schema,
gravação atômica de `data/receitas.json` e relatório. Ver [data-model.md](../data-model.md).
