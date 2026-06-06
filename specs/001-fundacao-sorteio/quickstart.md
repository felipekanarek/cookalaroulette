# Quickstart — Fase 1 — Fundação

**Feature**: 001-fundacao-sorteio · **Date**: 2026-06-05

Como rodar, testar e evoluir o Cook à la Roulette na Fase 1. Sem instalar nada além de
Python 3 (já presente) — não há build nem dependências.

## Rodar o site localmente

A página lê `data/receitas.json` via `fetch`, então **não** abra `index.html` por
`file://` (o navegador bloqueia por CORS). Sirva os arquivos por HTTP:

```bash
cd /Users/infoprice/cookAlaRoulette
python3 -m http.server 8000
```

Abra no navegador:

```
http://localhost:8000/
```

Clique em **"O que vou cozinhar?"** → a roleta anima por ~0,8s → você é levado a uma
receita real, em uma nova aba.

## Rodar o teste de distribuição do sorteio

Valida SC-003 (cada Chef dentro de ±10% da frequência esperada em ≥1000 sorteios) e que a
receita sorteada pertence ao Chef sorteado. Usa só o `assert` nativo do Node — sem
framework:

```bash
node tests/sorteio.test.js
```

Saída esperada: todas as asserções passam (exit 0).

## Verificações manuais (aceite)

- **US1 (P1)**: clicar leva a uma receita real e funcional no domínio de um Chef da lista.
- **US2 (P2)**: rodar o teste de distribuição acima.
- **US3 (P3)**: redimensionar o navegador para largura de celular e de desktop — imagem e
  botão centrados, sem rolagem horizontal.
- **FR-013**: clicar várias vezes rápido durante a animação — só um sorteio acontece.
- **FR-008 / FR-014**: testar os dois estados —
  - *vazio*: trocar `data/receitas.json` por `[]` → mensagem "sem receitas no momento".
  - *falha*: trocar por conteúdo inválido (ex.: `{`) → mensagem distinta de erro de carga.
- **FR-015 (acessibilidade)**: navegar até o botão com Tab (foco visível), acionar com
  Enter/Espaço; conferir que a imagem tem `alt`.

## Adicionar um Chef ou receita

Edite `data/receitas.json` e acrescente registros no formato do contrato
([receitas.schema.json](./contracts/receitas.schema.json)):

```json
{ "chef": "Nome", "site": "dominio.com", "titulo": "Receita", "url": "https://dominio.com/receita" }
```

Nenhuma mudança de código é necessária (Princípio VIII — escala por adição). Recarregue a
página.

## O que NÃO faz parte desta fase

`scrapers/` e `orquestrador.py` (coleta automatizada) são a Fase 2 — `scrapers/README.md`
apenas documenta o contrato que eles deverão cumprir. Design final e deploy público são a
Fase 4.
