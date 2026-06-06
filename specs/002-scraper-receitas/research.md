# Research — Fase 2 — Scraper (indexação automatizada)

**Date**: 2026-06-05 · **Feature**: 002-scraper-receitas

Decisões técnicas da Fase 0, todas dentro da stack autorizada pela constituição v2.0.0
(Python + BeautifulSoup + Playwright + parser de sitemap; deps restritas a coleta).

---

## 1. Cliente HTTP e "boa cidadania"

**Decision**: `requests` com um `User-Agent` realista e identificável, `timeout` por
requisição, pequeno atraso entre páginas e algumas tentativas com backoff em erros
transitórios (5xx/timeout).

**Rationale**: `requests` é simples e didático; o ritmo moderado + UA honesto respeitam os
sites de terceiros (a coleta é experimento de aprendizado, não carga). Backoff evita
falhas espúrias por instabilidade momentânea.

**Alternatives considered**: `httpx` (assíncrono) — mais rápido, mas concorrência
complica o aprendizado e a cortesia; rejeitado para esta fase.

---

## 2. Ordem de técnicas por site (sitemap → BeautifulSoup → Playwright)

**Decision**: `base.py` oferece as três técnicas; cada adaptador declara a ordem que tenta.
(1) **Sitemap**: ler `robots.txt` para achar `Sitemap:`, senão `dominio.com/sitemap.xml`;
seguir índices de sitemap aninhados; filtrar URLs de receita por padrão do site. (2)
**BeautifulSoup**: parsear páginas de listagem e extrair links de receita. (3)
**Playwright**: abrir navegador real quando o conteúdo depende de JS ou quando há bloqueio.

**Rationale**: sitemap é a fonte mais completa e barata (aprendizado central do briefing —
o caso RecipeTin Eats); só escala para BS4/Playwright quando necessário.

**Alternatives considered**: ir direto a Playwright em tudo — lento e desnecessário;
rejeitado (viola "preferir a técnica mais simples").

---

## 3. Filtro de URLs de receita (por site)

**Decision**: cada adaptador conhece o padrão de URL de receita do seu site e descarta
listagens/categorias. Padrões iniciais a validar na implementação:
- **panelinha.com.br** → caminho contém `/receita/`
- **jamieoliver.com** → `/recipes/<categoria>/<slug>/` (excluir `/recipes/` raiz e categorias)
- **recipetineats.com** → slug de nível raiz (`/<slug>/`), excluindo páginas institucionais
- **seriouseats.com** → caminho de receita (ex.: contém `-recipe-` ou seção de receitas)
- **maangchi.com** → `/recipe/<slug>`

**Rationale**: filtro por site mantém o ruído fora; cada padrão é simples e testável.

**Alternatives considered**: heurística genérica única para todos os sites — frágil entre
estruturas tão diferentes; rejeitada.

---

## 4. Título da receita sem violar o Princípio III

**Decision**: o `titulo` é o **nome** da receita — obtido do texto do link na listagem, do
`<title>`/`<h1>` da página, ou do `<loc>`/slug do sitemap. Nenhum outro conteúdo (texto da
receita, ingredientes, modo de preparo, fotos, vídeo) é lido para armazenamento.

**Rationale**: o nome é um rótulo de localização (faz parte do contrato `{chef, site,
titulo, url}`), não o conteúdo da receita. Respeita "indexar onde está, não o que contém".

---

## 5. Site bloqueado (HTTP 403 / anti-bot) — FR-009

**Decision**: ao detectar bloqueio (403/429 ou resposta de desafio), tentar **um** fallback
via Playwright (navegador real, headers/JS legítimos). Se ainda assim bloquear, **pular o
site e registrar** no relatório, sem abortar a coleta dos demais. (Aprendizado real:
`maangchi.com` respondeu 403 ao `requests` nesta sessão.)

**Rationale**: dá uma chance honesta (navegador real costuma passar onde o `requests`
falha) sem entrar em guerra anti-bot (fora de escopo). Falha isolada não derruba a rodada.

**Alternatives considered**: contornar agressivamente (rotação de IP, resolver CAPTCHA) —
fora de escopo e eticamente duvidoso; rejeitado.

---

## 6. Verificação de URLs vivas antes de gravar — FR-015

**Decision**: para cada URL coletada, fazer um **HEAD** (com fallback para **GET** leve se o
servidor responder 405 ao HEAD), seguindo redirecionamentos; manter apenas as que terminam
em **2xx**. Descartar as demais e contar no relatório. Verificação com um pequeno pool de
threads para não ficar lento.

**Rationale**: é o que cumpre o propósito da fase (acabar com os links quebrados da Fase 1)
e o SC-004 (≥90% vivas). HEAD é barato; GET de fallback cobre servidores que recusam HEAD.

**Alternatives considered**: não verificar (rápido, mas reintroduz link morto) — rejeitado;
verificar por amostragem — deixa links mortos passarem; rejeitado.

---

## 7. Deduplicação e gravação atômica — FR-007, FR-012

**Decision**: deduplicar por **URL normalizada** (minúsculas no esquema/host, remover
fragmento `#...`, normalizar barra final). Gravar `data/receitas.json` escrevendo em arquivo
temporário e fazendo `os.replace` (atômico) — nunca deixa arquivo meio-escrito.

**Rationale**: dedup por URL evita repetições; normalização evita duplicatas triviais
(barra final/maiúsculas). `os.replace` é atômico no mesmo filesystem.

**Alternatives considered**: dedup por (titulo+chef) — arriscado (títulos repetem); rejeitado.

---

## 8. Validação do contrato sem dependência extra — FR-006, Princípio VI

**Decision**: validar cada registro em Python puro contra o contrato (campos `chef`, `site`,
`titulo`, `url` não-vazios; `url` casando `^https?://`), reusando como referência o schema
`specs/001-fundacao-sorteio/contracts/receitas.schema.json`. Não adicionar `jsonschema`.

**Rationale**: mantém as dependências restritas a ferramentas de coleta (Princípio VI); a
validação é simples o suficiente para Python puro.

---

## 9. Relatório de execução — FR-010

**Decision**: ao final, imprimir um resumo por site: técnica usada, coletadas, duplicatas
removidas, URLs mortas descartadas, e status (ok / bloqueado-pulado / sem-receitas). Sem
truncamento silencioso.

**Rationale**: observabilidade da coleta; deixa explícito o que entrou e o que ficou de
fora — essencial num experimento de scraping.
