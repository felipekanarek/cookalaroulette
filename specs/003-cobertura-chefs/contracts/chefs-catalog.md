# Catálogo de Chefs — Fase 3 (cobertura completa)

**Feature**: 003-cobertura-chefs · **Date**: 2026-06-05

Os 38 chefs / 25 países do briefing, com a **técnica inicial a tentar** por adaptador. A
técnica real é bespoke e confirmada na implementação (cada site é diferente). Todos
produzem o Contrato Único `{chef, site, titulo, url}` — ver
[../../002-scraper-receitas/contracts/adapter-contract.md](../../002-scraper-receitas/contracts/adapter-contract.md).

Técnicas: **S** = sitemap · **SB** = sitemap via navegador (sites bloqueados) · **L** =
crawl de listagem (sem sitemap) · técnica "a confirmar" = melhor palpite, valida-se ao codar.

| # | Chef | Domínio | País | Técnica inicial | Status |
|---|------|---------|------|-----------------|--------|
| 1 | Rita Lobo | panelinha.com.br | 🇧🇷 | **L** (sem sitemap) | ⚠️ Fase 2 (reescrever p/ listagem) |
| 2 | Bela Gil | belagil.com | 🇧🇷 | S (/conteudo/receitas/) | ✅ feito |
| 3 | Layla Pujol | laylita.com | 🇪🇨 | crawl de /recipes/index | ✅ feito |
| 4 | Cecilia Tupac | ceciliatupac.com | 🇵🇪 | S (Wix, /post/) | ✅ feito |
| 5 | Paulina Cocina | paulinacocina.net | 🇦🇷 | S (slug/id; algum ruído) | ✅ feito |
| 6 | Pati Jinich | patijinich.com | 🇲🇽 | **crawl** de /recipes/ (post-sitemap é poluído c/ mídia) | ✅ feito |
| 7 | Jamie Oliver | jamieoliver.com | 🇬🇧 | S + stoplist | ✅ feito |
| 8 | Nigella Lawson | nigella.com | 🇬🇧 | S (/recipes/, só autorais) | ✅ feito |
| 9 | Gordon Ramsay | gordonramsay.com | 🇬🇧 | SB (provável bloqueio) | ⏳ |
| 10 | Yotam Ottolenghi | ottolenghi.co.uk | 🇬🇧 | crawl (Shopify /pages/recipes/) | ✅ feito |
| 11 | Donal Skehan | donalskehan.com | 🇮🇪 | S (recipes-sitemap) | ✅ feito |
| 12 | Kenji López-Alt | seriouseats.com | 🇺🇸 | **wayback** (Cloudflare → Internet Archive) | ✅ feito |
| 13 | Deb Perelman | smittenkitchen.com | 🇺🇸 | S (/AAAA/MM/slug) | ✅ feito |
| 14 | Tieghan Gerard | halfbakedharvest.com | 🇺🇸 | S (a confirmar) | ⏳ |
| 15 | Joshua Weissman | joshuaweissman.com | 🇺🇸 | S (a confirmar) | ⏳ |
| 16 | Ina Garten | barefootcontessa.com | 🇺🇸 | S/L (a confirmar) | ⏳ |
| 17 | Akis Petretzikis | akispetretzikis.com | 🇬🇷 | SB (/en/recipe/) | ✅ feito |
| 18 | David Lebovitz | davidlebovitz.com | 🇫🇷 | **wayback** (filtro recipe/recette) | ✅ feito |
| 19 | Vincenzo's Plate | vincenzosplate.com | 🇮🇹 | crawl | ✅ feito |
| 20 | Flavia Imperatore (Misya) | misya.info | 🇮🇹 | S (/ricetta/*.htm) | ✅ feito |
| 21 | Omar Allibhoy | thespanishchef.com | 🇪🇸 | S (/recipes/) | ✅ feito |
| 22 | Joanna (Kwestia Smaku) | kwestiasmaku.com | 🇵🇱 | crawl (Drupal, /przepis.html) | ✅ feito |
| 23 | Dorota Ś. (Moje Wypieki) | mojewypieki.com | 🇵🇱 | S (a confirmar) | ⏳ |
| 24 | Natasha Kravchuk | natashaskitchen.com | 🇺🇦 | S (slug exige '-recipe') | ✅ feito |
| 25 | Nevada Berg | northwildkitchen.com | 🇳🇴 | crawl | ✅ feito |
| 26 | Trine Hahnemann | trinehahnemann.com | 🇩🇰 | S (recipe post-type, 41) | ✅ feito |
| 27 | Linda Lomelino | callmecupcake.se | 🇸🇪 | S (Blogger /YYYY/MM) | ✅ feito |
| 28 | Ozoz Sokoh | kitchenbutterfly.com | 🇳🇬 | crawl (ruído em volume) | ✅ feito |
| 29 | Zoe Adjonyoh | zoesghana.com | 🇬🇭 | domínio MORTO (à venda) | ⛔ sem dados |
| 30 | Alida Ryder | simply-delicious-food.com | 🇿🇦 | S (slug-raiz) | ✅ feito |
| 31 | Maangchi | maangchi.com | 🇰🇷 | SB (bloqueado) | ✅ feito |
| 32 | Namiko Chen | justonecookbook.com | 🇯🇵 | SB (slug-raiz) | ✅ feito |
| 33 | The Woks of Life | thewoksoflife.com | 🇨🇳 | S (sem www) | ✅ feito |
| 34 | Sanjeev Kapoor | sanjeevkapoor.com | 🇮🇳 | crawl (/Recipe/) | ✅ feito |
| 35 | Pailin Chongchitnant | hot-thai-kitchen.com | 🇹🇭 | **wayback** (slug-raiz) | ✅ feito |
| 36 | Helen Le | **helenrecipes.com** (danangcuisine morto) | 🇻🇳 | S | ✅ feito |
| 37 | Nagi Maehashi | recipetineats.com | 🇦🇺 | S (post-sitemaps) | ✅ feito |
| 38 | Adam Liaw | adamliaw.com | 🇦🇺 | crawl da home (Next.js) | ✅ feito |

## Lotes de implementação sugeridos

- **Lote 0 (pendentes da Fase 2)**: Panelinha (L) + Serious Eats (SB) — destravam as 2 técnicas que faltam.
- **Lote 1 — sitemap "fácil"** (WordPress/Yoast): a maioria dos blogs (Bela Gil, Laylita, Pati Jinich, Smitten Kitchen, Half Baked Harvest, Just One Cookbook, Woks of Life, Natasha's Kitchen, etc.). Reusa `coletar_por_sitemap` (+ sub-filtro de posts/stoplist conforme o caso).
- **Lote 2 — bloqueados**: Gordon Ramsay, Sanjeev Kapoor e quaisquer que respondam 403 → `coletar_por_sitemap_browser`.
- **Lote 3 — sem sitemap**: os que não expõem sitemap → `coletar_por_listagem`.

> A técnica "a confirmar" é validada por adaptador ao implementar (sondar robots.txt/sitemap,
> testar requests vs. bloqueio). É a natureza bespoke do scraping (Princípio VII).

## Sondagem do Lote 1 (2026-06-05) — onde retomar

Sondei 8 candidatos diversos. Achados (poupa re-sondar):

| Chef / site | Achado | Técnica indicada |
|-------------|--------|------------------|
| Pati Jinich (patijinich.com) | sitemap_index acessível, receitas em **slug de raiz** | S — padrão RTE (post-sitemap + stoplist) ✅ pronto pra escrever |
| Natasha's Kitchen (natashaskitchen.com) | sitemap_index acessível, slug de raiz | S — padrão RTE ✅ pronto pra escrever |
| The Woks of Life (thewoksoflife.com) | **www dá 404** | S — usar `https://thewoksoflife.com` (sem www) e re-sondar |
| Laylita (laylita.com) | tem /sitemap.xml mas conteúdo **misturado** (blog/wine/receita) | S — precisa descobrir o padrão de URL de receita |
| David Lebovitz (davidlebovitz.com) | **403 (bloqueado)** | SB — `coletar_por_sitemap_browser` (como Maangchi) |
| Just One Cookbook (justonecookbook.com) | **403 (bloqueado)** | SB |
| Akis Petretzikis (akispetretzikis.com) | **403 (bloqueado)** | SB |
| Hot Thai Kitchen (hot-thai-kitchen.com) | **403 (bloqueado)** | SB |

**Próximo passo concreto**: escrever `scrapers/patijinich.py` e `scrapers/natashaskitchen.py`
(padrão RTE: `coletar_por_sitemap` com `sub_filtro` de post-sitemap + filtro de slug de raiz
com stoplist), registrá-los no `orquestrador.py`, rodar e validar. Depois os 4 bloqueados via
`coletar_por_sitemap_browser` (o helper já existe e está provado na Maangchi).

> Nota: vários blogs respondem 403 ao `requests` mas o helper de navegador costuma passar —
> a Serious Eats é exceção (Cloudflare bloqueia até headless; pulada).
