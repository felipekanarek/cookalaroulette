<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/006-dominio-seo/plan.md`

Project: **Cook à la Roulette** — sorteador de receitas que redireciona para o site
original do Chef. Frontend: HTML/CSS/JS puro (sem frameworks, sem build) — tela tipográfica
clicável, fonte aleatória do Google Fonts (constituição v2.0.1). Scraper (Fase 2): Python +
BeautifulSoup + Playwright, adaptadores por site em `scrapers/` + `orquestrador.py`, gerando
`data/receitas.json` no contrato `{chef, site, titulo, url}`. Constituição em
`.specify/memory/constitution.md`. Active feature: `006-dominio-seo` (Fase 6 — domínio próprio cookalaroulette.com já no ar com HTTPS; falta SEO/encontrabilidade: title/description EN, canonical, JSON-LD Schema.org, robots.txt, sitemap.xml, Search Console + GoatCounter como analytics privacy-friendly com evento `roleta-clique`). Repo no ar em https://cookalaroulette.com.
<!-- SPECKIT END -->
