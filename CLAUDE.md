<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:
`specs/005-expansao-cobertura/plan.md`

Project: **Cook à la Roulette** — sorteador de receitas que redireciona para o site
original do Chef. Frontend: HTML/CSS/JS puro (sem frameworks, sem build) — tela tipográfica
clicável, fonte aleatória do Google Fonts (constituição v2.0.1). Scraper (Fase 2): Python +
BeautifulSoup + Playwright, adaptadores por site em `scrapers/` + `orquestrador.py`, gerando
`data/receitas.json` no contrato `{chef, site, titulo, url}`. Constituição em
`.specify/memory/constitution.md`. Active feature: `005-expansao-cobertura` (Fase 5 — adicionar ~58 novos sites/chefs da Lista 2 ao scraper via adaptadores, integrando ao catálogo com o modo cirúrgico `--site`; só scraper, contrato inalterado). Repo já publicado e no ar via GitHub Pages.
<!-- SPECKIT END -->
