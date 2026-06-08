# Data Model — Domínio próprio + SEO (Fase 6)

Esta fase **não introduz entidades de dados** (não há banco, não há novo formato no
`receitas.json`). O "modelo" aqui é declarativo: artefatos estáticos que sinalizam ao mundo
quem somos. Documentado para referência.

## Entidades declarativas

### Homepage (`index.html`) — INALTERADA no `<body>`, ALTERADA no `<head>`

| Atributo no `<head>` | Tipo | Valor (resumo) |
|----------------------|------|----------------|
| `<title>` | string | "Cook à la Roulette — what should I cook today?" |
| `<meta name="description">` | string | descrição EN ~155 chars (ver contrato) |
| `<link rel="canonical">` | URL | `https://cookalaroulette.com/` |
| `<meta property="og:*">` | grupo | URLs absolutas pro domínio novo |
| `<meta name="twitter:*">` | grupo | URLs absolutas pro domínio novo |
| `<meta name="google-site-verification">` | string | token do GSC (placeholder até Felipe gerar) |
| `<script application/ld+json>` | JSON | Schema.org `WebSite` |
| `<script data-goatcounter>` | external | snippet do GoatCounter (async) |

Restrição transversal: **nada no `<body>` muda** (Princípio I).

### `app.js` — ALTERADO em 1 ponto

| Local | Mudança |
|-------|---------|
| `aoClicar()` | +1 linha best-effort: `try { window.goatcounter && goatcounter.count({event:true, path:'roleta-clique'}); } catch(_){}` |

Comportamento do sorteio e do redirect: inalterado. A chamada é não-bloqueante e ignorada se o
GoatCounter não estiver carregado (ad-blocker, offline, etc.).

### Arquivos novos na raiz

| Arquivo | Tipo | Conteúdo (resumo) |
|---------|------|-------------------|
| `robots.txt` | texto plano | `User-agent: *` + `Allow: /` + `Sitemap: https://cookalaroulette.com/sitemap.xml` |
| `sitemap.xml` | XML | 1 `<url>` com `<loc>` da homepage canônica + `<lastmod>` |
| `CNAME` | texto plano | `cookalaroulette.com` (✅ **já existe** — criado pelo GitHub) |

### Contas externas (estado fora do repo)

| Conta | Propósito | Quem gerencia |
|-------|-----------|---------------|
| Google Search Console | Verificar propriedade + submeter sitemap + monitorar | Felipe (manual, uma vez) |
| GoatCounter | Painel de visitas + cliques | Felipe (manual, uma vez) |
| Hostgator (DNS) | DNS do domínio | Felipe (já feito) |
| GitHub Pages | Hospedagem | Felipe (já feito) |

## Invariantes

- INV-1: `<body>` byte-equivalente entre antes e depois (modulo a roleta de fontes da Fase 4).
- INV-2: nenhum cookie criado pelo site (verificável com DevTools → Application → Cookies).
- INV-3: nenhum bloqueio do render do `<body>` pelo script do GoatCounter (carrega async).
- INV-4: o sorteio + redirect funcionam mesmo com o GoatCounter falhando (try/catch + best-effort).
- INV-5: `data/receitas.json` e `scrapers/*` byte-equivalentes ao estado atual (Princípio IV).
- INV-6: o produto continua redirecionando para receitas dos chefs — nenhum conteúdo de receita
  é exposto no site (Princípio III).
