<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/003-cobertura-chefs/plan.md`

Project: **Cook a la Roulette** — sorteador de receitas que redireciona para o site
original do Chef. Frontend: HTML/CSS/JS puro (sem frameworks, sem build) — tela tipográfica
clicável, fonte aleatória do Google Fonts (constituição v2.0.0). Scraper (Fase 2): Python +
BeautifulSoup + Playwright, adaptadores por site em `scrapers/` + `orquestrador.py`, gerando
`data/receitas.json` no contrato `{chef, site, titulo, url}`. Constituição em
`.specify/memory/constitution.md`. Active feature: `003-cobertura-chefs` (Fase 3 — cobertura completa: 38 chefs, helpers de sitemap-via-navegador e crawl de listagem).
<!-- SPECKIT END -->
