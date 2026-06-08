# Implementation Plan: Domínio próprio + SEO

**Branch**: `006-dominio-seo` | **Date**: 2026-06-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-dominio-seo/spec.md`

## Summary

Concluir a Fase 6 do Cook à la Roulette: o **Pilar 1 (domínio próprio + HTTPS)** já está no ar
em `https://cookalaroulette.com` (DNS na Hostgator, GitHub Pages Custom Domain, Enforce HTTPS
ativo, redirects 301 validados a partir de `http://`, `https://www.` e `.github.io/cookalaroulette/`).
Resta o **Pilar 2 (SEO honesto)**: enriquecer o `<head>` da homepage com `<title>`/`<meta
description>` em inglês, `<link rel="canonical">`, JSON-LD Schema.org `WebSite`, atualizar OG/
Twitter para o domínio novo, meta `google-site-verification`, e adicionar o snippet do
**GoatCounter** (analytics privacy-friendly) com evento custom `roleta-clique` disparado pelo
handler de clique em `app.js`. Criar `robots.txt` e `sitemap.xml` na raiz. Atualizar URLs absolutas
em README/repo metadata. Cadastrar a propriedade no Google Search Console e submeter o sitemap.

Tudo respeita Minimalismo Radical: zero elemento visível novo na tela. Frontend continua
HTML/CSS/JS puro. Scraper, contrato `{chef, site, titulo, url}` e `data/receitas.json`
intocados (Princípio IV).

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript (ES6+) puros — sem framework, sem build.
**Primary Dependencies**: GitHub Pages (hospedagem estática), Google Fonts via CDN (já em uso,
exceção constitucional documentada). Nova dependência externa: **GoatCounter** (script `gc.zgo.at/count.js`).
**Storage**: arquivos estáticos no repo (`index.html`, novos `robots.txt`, `sitemap.xml`, `CNAME` já presente).
**Testing**: validação manual via curl/dig/navegador + Lighthouse SEO + Search Console (UI).
Não há testes automatizados de SEO (out of scope — verificável manualmente).
**Target Platform**: navegadores modernos (mesma matriz das Fases anteriores); crawlers de
busca (Googlebot, Bingbot etc.).
**Project Type**: site estático single-page hospedado em GitHub Pages com domínio próprio.
**Performance Goals**: TTFB ≤ 500ms (servido pelo Pages com gzip); LCP ≤ 2,5s 4G típico
(SC-001 ≤ 2s; o catálogo `receitas.json` é ~2 MB gzip — carrega após a tela ser pintada).
**Constraints**: zero elemento visível novo (Princípio I); zero cookies de terceiros (GoatCounter
é cookieless); script externo deve ser async + falha-silenciosa (não pode quebrar o sorteio).
**Scale/Scope**: 1 página HTML, 3 arquivos novos auxiliares (`robots.txt`, `sitemap.xml`,
meta google-site-verification já no `<head>`); 1 chamada JS adicionada ao `aoClicar`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Conformidade |
|-----------|--------------|
| I. Minimalismo Radical (UX) | ✅ Nada visível novo. Toda alteração no `<head>` + arquivos auxiliares (`robots.txt`, `sitemap.xml`, `CNAME`). |
| II. Zero Fricção | ✅ GoatCounter é cookieless, sem banner de consentimento. Async, não bloqueia render. |
| III. Redirecionar, Nunca Hospedar | ✅ Nenhum conteúdo de receita exposto. Sitemap só lista a homepage. |
| IV. Separação Estrita Scraper ↔ Frontend | ✅ Mexe só em `index.html`, `app.js` (1 linha), novos arquivos estáticos, README, repo metadata. Scraper/`receitas.json` intocados. |
| V. Contrato Único dos Adaptadores | ✅ N/A — não toca adaptadores. |
| VI. Fundamentos sem Frameworks | ⚠️ **Exceção documentada**: snippet do GoatCounter (~3 KB, 1 `<script>` externo). Mesmo espírito da exceção já aberta para Google Fonts via CDN (stylesheet/serviço externo simples, sem framework, sem build). |
| VII. Aprendizado em Primeiro Lugar | ✅ Tudo é HTML puro + 1 chamada JS — sem caixa-preta. |
| VIII. Escala por Adição | ✅ N/A — não toca catálogo. |

**Resultado do gate: PASS** com uma exceção registrada no Princípio VI (GoatCounter via CDN, documentada em Complexity Tracking abaixo e em Assumptions da spec).

## Project Structure

### Documentation (this feature)

```text
specs/006-dominio-seo/
├── plan.md              # Este arquivo (/speckit-plan)
├── research.md          # Phase 0 — decisões finas (texto do title/meta, formato JSON-LD, método de verificação GSC, slug GoatCounter)
├── data-model.md        # Phase 1 — entidades (artefatos SEO no <head>, arquivos auxiliares, conta externa)
├── contracts/
│   ├── seo-meta.md      # Phase 1 — contrato dos elementos do <head> (title, description, canonical, JSON-LD, OG, twitter, google-site-verification, goatcounter)
│   ├── robots.md        # Phase 1 — contrato do robots.txt
│   └── sitemap.md       # Phase 1 — contrato do sitemap.xml
├── quickstart.md        # Phase 1 — como executar/validar a fase
├── checklists/
│   └── requirements.md  # checklist de qualidade da spec (já criado, ✅)
└── tasks.md             # Phase 2 (/speckit-tasks — NÃO criado aqui)
```

### Source Code (repository root)

```text
index.html               # ALTERADO: novas tags no <head> (title/description EN, canonical,
                         #   JSON-LD, OG/Twitter URLs atualizadas, google-site-verification,
                         #   <script> do GoatCounter). <body> INALTERADO.
app.js                   # ALTERADO: +1 linha no aoClicar() disparando o evento 'roleta-clique'.
                         #   Comportamento do sorteio/redirect INALTERADO.
robots.txt               # NOVO: allow geral + Sitemap: https://cookalaroulette.com/sitemap.xml
sitemap.xml              # NOVO: 1 entry — homepage canônica + lastmod.
CNAME                    # JÁ EXISTE (criado pelo GitHub ao configurar Custom Domain).
README.md                # ALTERADO: URLs atualizadas para o domínio novo + nota da Fase 6.
style.css, sorteio.js    # INTOCADOS.
data/receitas.json       # INTOCADO (Princípio IV).
scrapers/*, orquestrador.py # INTOCADOS (Princípio IV).
```

**Structure Decision**: a fase **só adiciona conteúdo declarativo** ao `<head>` da página
existente e cria 2 arquivos estáticos novos na raiz (`robots.txt`, `sitemap.xml`). A única
mudança comportamental no JS é a chamada `goatcounter.count(...)` no handler do clique — em
linha única, best-effort, sem afetar o sorteio. Nenhum diretório novo, nenhum build.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| GoatCounter via CDN (`<script>` externo) — exceção ao Princípio VI | Visibilidade básica de uso (visitas + cliques) que o mantenedor pediu explicitamente; sem isso, o produto fica "publicado no escuro" | (a) **Zero analytics**: rejeitado pelo dono do projeto após reflexão — quer saber quantos acessos/cliques. (b) **Self-host** (Umami): exige rodar um servidor, fricção operacional alta para 1 site estático. (c) **Cloudflare Web Analytics**: não suporta evento custom (cliques) no tier free. (d) **Plausible**: US$ 9/mês, custo desnecessário para um projeto pessoal. **GoatCounter free é o mínimo necessário**: 1 `<script>` async (~3 KB), sem cookies, sem banner LGPD/GDPR, open-source. Mesma natureza da exceção já aberta no Princípio VI para Google Fonts via CDN. |
