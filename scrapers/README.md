# scrapers/ — adaptadores de coleta

Um adaptador por site (`scrapers/<site>.py`); o `../orquestrador.py` chama todos, consolida,
deduplica por URL, verifica URLs vivas e grava `data/receitas.json`. Separação Estrita
(Princípio IV): o scraper só escreve o JSON; o frontend não é tocado. Coleta **apenas a
localização** da receita — nunca o conteúdo (Princípio III).

## Contrato Único (Princípio V)

Todo adaptador expõe `CHEF`, `SITE`, `TECNICAS` e `coletar(limite) -> list[dict]`, retornando
registros no mesmo formato, qualquer que seja a técnica interna:

```json
{ "chef": "Jamie Oliver", "site": "jamieoliver.com", "titulo": "Spaghetti Carbonara",
  "url": "https://www.jamieoliver.com/recipes/pasta-recipes/spaghetti-carbonara/" }
```

Schema: [`../specs/001-fundacao-sorteio/contracts/receitas.schema.json`](../specs/001-fundacao-sorteio/contracts/receitas.schema.json).

## Helpers compartilhados (`base.py`)

Cada adaptador é pequeno: declara o padrão de URL de receita do site (`_e_receita`) e chama
um helper. As cinco técnicas, da mais simples à mais pesada:

| Helper | Quando usar |
|--------|-------------|
| `coletar_por_sitemap(...)` | site tem sitemap acessível (preferido); `sub_filtro` p/ pegar só post-sitemaps |
| `coletar_por_listagem(...)` | sem sitemap, mas há página(s) de listagem com links de receita |
| `coletar_por_crawl(...)` | sem sitemap/listagem indexável → BFS seguindo "receitas relacionadas" |
| `coletar_por_sitemap_browser(...)` | site bloqueia o cliente HTTP (403) mas o sitemap abre via navegador (Playwright) |
| `coletar_por_wayback(...)` | site atrás de Cloudflare → descobre URLs pelo Internet Archive (CDX), sem tocar no site |

Regra (constituição): preferir sempre a técnica mais simples que entregue receitas limpas.
A escolha é **bespoke por site** — sondar `robots.txt`/sitemap e `requests` vs. 403 antes.

## Status dos adaptadores

A tabela completa (38 Chefs, técnica e status) está em
[`../specs/003-cobertura-chefs/contracts/chefs-catalog.md`](../specs/003-cobertura-chefs/contracts/chefs-catalog.md).

Resumo: ~30 adaptadores funcionando, cobrindo 25+ países, com as 5 técnicas acima.
**Fora**: `zoesghana` (domínio morto). Os ex-bloqueados por Cloudflare (Serious Eats, David
Lebovitz, Hot Thai Kitchen) usam a técnica **wayback**.

## Adicionar um Chef (Princípio VIII — escala por adição)

1. Criar `scrapers/<site>.py` com `CHEF`/`SITE`/`TECNICAS`, um `_e_receita(url)` para o padrão
   de URL daquele site, e `coletar(limite)` chamando o helper adequado.
2. Importar e incluir o módulo em `ADAPTADORES` no `../orquestrador.py`.
3. Testar isolado: `python3 -c "from scrapers import <site> as m; print(m.coletar(8))"`.

Nada mais muda — nem os outros adaptadores, nem o frontend.
