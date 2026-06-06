# Data Model — Fase 1 — Fundação

**Date**: 2026-06-05 · **Feature**: 001-fundacao-sorteio

## Visão geral

A única fonte de dados é `data/receitas.json`: um **array plano** de registros de receita.
O formato do registro é o **Contrato Único dos Adaptadores** (Princípio V) — o mesmo que os
scrapers da Fase 2 produzirão. O frontend não persiste nada; apenas lê.

## Entidade: Receita curada (registro do JSON)

Cada item do array é um objeto com exatamente estes campos:

| Campo | Tipo | Obrigatório | Regras de validação |
|-------|------|-------------|---------------------|
| `chef` | string | sim | Não-vazio após `trim`. Nome de quem assina a receita. |
| `site` | string | sim | Não-vazio. Domínio de origem (ex.: `panelinha.com.br`). |
| `titulo` | string | sim | Não-vazio. Título da receita. |
| `url` | string | sim | URL absoluta `http(s)://` válida e não-vazia. |

**Exemplo de registro:**

```json
{
  "chef": "Rita Lobo",
  "site": "panelinha.com.br",
  "titulo": "Arroz de forno",
  "url": "https://www.panelinha.com.br/receita/arroz-de-forno"
}
```

**Exemplo de arquivo (`data/receitas.json`):**

```json
[
  { "chef": "Rita Lobo", "site": "panelinha.com.br", "titulo": "Arroz de forno", "url": "https://www.panelinha.com.br/receita/arroz-de-forno" },
  { "chef": "Jamie Oliver", "site": "jamieoliver.com", "titulo": "Spaghetti Carbonara", "url": "https://www.jamieoliver.com/recipes/pasta-recipes/spaghetti-carbonara/" },
  { "chef": "Maangchi", "site": "maangchi.com", "titulo": "Bibimbap", "url": "https://www.maangchi.com/recipe/bibimbap" }
]
```

## Entidade derivada (em memória): Chef

Não existe no JSON como objeto próprio — é **derivada** agrupando os registros por `chef` no
carregamento. Usada como a primeira etapa do sorteio.

| Propriedade | Origem | Uso |
|-------------|--------|-----|
| `nome` | valor distinto de `chef` | chave de agrupamento e unidade do 1º sorteio |
| `receitas` | registros com aquele `chef` | conjunto do 2º sorteio |

- **Identidade**: um Chef é identificado pelo valor de `chef` (string). Registros com o
  mesmo `chef` pertencem ao mesmo Chef.
- **Elegibilidade para sorteio**: só entram Chefs com ≥1 receita **válida** (URL válida).

## Regras aplicadas no carregamento (FR-002, FR-007)

1. Ler e parsear o array de registros.
2. Descartar registros inválidos (qualquer campo obrigatório vazio ou `url` não-`http(s)`).
3. Agrupar os registros válidos por `chef`.
4. Descartar Chefs que ficaram sem nenhuma receita válida.
5. Resultado: um mapa `Chef → [receitas válidas]` pronto para o sorteio em duas etapas.

## Estados do conjunto de dados (FR-008, FR-014)

| Estado | Condição | Comportamento |
|--------|----------|---------------|
| OK | ≥1 Chef elegível após filtragem | botão habilitado; sorteio disponível |
| Vazio | carregou, mas 0 receitas válidas | mensagem "sem receitas no momento"; botão desabilitado |
| Falha | erro de rede/HTTP, JSON malformado ou raiz não-array | mensagem distinta "não foi possível carregar as receitas agora"; botão desabilitado |

## Sem estado persistente

Não há histórico, contadores nem prevenção de repetição (Princípio I; Assumption "sem
memória entre sorteios"). Cada sorteio é independente.
