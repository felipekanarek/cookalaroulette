# Research — Fase 3 — Ampliação de cobertura

**Date**: 2026-06-05 · **Feature**: 003-cobertura-chefs

Decisões da Fase 0, todas reusando a stack da Fase 2 (sem novas dependências).

---

## 1. Helper reutilizável: sitemap via navegador real

**Decision**: Generalizar a lógica que funcionou na Maangchi em `base.coletar_por_sitemap_browser(base_url, chef, site, url_e_receita, limite, *, sub_filtro=None)`:
abre Chromium, busca o sitemap pelo **corpo bruto da resposta** (`resp.text()`, não o DOM
renderizado), recursa em índices de sitemap, aplica o filtro de URL.

**Rationale**: É o padrão para sites bloqueados (403) que têm sitemap atrás do anti-bot.
Evita reescrever em cada adaptador. Lição-chave: o Chromium renderiza XML como árvore
visual — `page.content()` não traz os `<loc>`; só `response.text()`.

**Alternatives considered**: copiar o código da Maangchi em cada adaptador — viola DRY e o
Princípio VIII; rejeitado.

---

## 2. Helper reutilizável: crawl de listagem (sites sem sitemap)

**Decision**: `base.coletar_por_listagem(urls_listagem, chef, site, url_e_receita, limite, *, usar_browser=False)`:
busca uma ou mais páginas de listagem (com `requests`+BS4 por padrão; Playwright se
`usar_browser=True` ou se detectar que a listagem é JS), extrai `<a href>`, normaliza para
absoluto, filtra com `url_e_receita`, monta registros (título do texto do link ou do slug).

**Rationale**: Cobre sites sem sitemap (ex.: Panelinha). BS4 primeiro (leve), browser só
quando necessário — escalonamento coerente com "técnica mais simples que funcione".

**Alternatives considered**: sempre browser (lento/pesado) — rejeitado; só BS4 (falha em
listagens JS) — rejeitado.

---

## 3. Catálogo de chefs e técnica planejada

**Decision**: Mapear os 38 chefs → domínio → técnica inicial a tentar, em
[contracts/chefs-catalog.md](./contracts/chefs-catalog.md). A maioria são blogs
WordPress/Yoast (sitemap de posts). A técnica real é confirmada por adaptador na
implementação (cada site é bespoke).

**Rationale**: Organiza os ~35 adaptadores em lotes por técnica, dá visão de cobertura e
evita "descobrir do zero" cada site no meio da implementação.

---

## 4. Coleta educada em escala

**Decision**: Manter `User-Agent` identificável + pausa entre requisições; aplicar um
**timeout por adaptador** no orquestrador para um site lento/preso não travar a rodada
inteira; manter o teto por site (~50). Playwright reusa uma instância por adaptador.

**Rationale**: 38 sites podem somar muitos minutos; timeouts e teto mantêm a rodada
previsível e cortês. Falha/timeout de um site → reportado e pulado (FR-008).

**Alternatives considered**: paralelismo agressivo entre sites — mais rápido, porém menos
cortês e mais frágil; adiado (a verificação de URLs já usa um pool pequeno).

---

## 5. Idiomas e títulos

**Decision**: `humanizar_slug` continua derivando o título do slug (funciona com slugs
acentuados/multilíngues). Quando a listagem trouxer o texto do link, preferir esse texto
como título (mais fiel que o slug).

**Rationale**: A curadoria é internacional (PT, ES, EL, PL, JP, KR, ZH...). O nome é só um
rótulo (Princípio III); slug humanizado é suficiente, texto do link é melhor quando há.

---

## 6. Re-indexação (FR-011)

**Decision**: Manual sob demanda — `python orquestrador.py`. Documentar no quickstart como
agendar no futuro (ex.: `cron` mensal chamando o orquestrador no venv). Sem automação agora.

**Rationale**: Simples e suficiente para a fase; a porta para agendar fica aberta sem
mudar arquitetura.

---

## 7. Resiliência da rodada

**Decision**: Reusar as garantias da Fase 2 — try/except por adaptador (bloqueio→pulado,
erro→reportado), dedup por URL, verificação de URL viva (403/401/429 = existe), gravação
atômica e **nunca sobrescrever com vazio**. Adicionar timeout por adaptador.

**Rationale**: Com 38 sites, falhas parciais são esperadas; a rodada deve sempre terminar
com um `receitas.json` consolidado e útil.
