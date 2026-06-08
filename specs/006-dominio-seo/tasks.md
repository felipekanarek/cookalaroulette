# Tasks: Domínio próprio + SEO

**Feature**: `006-dominio-seo` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Contexto: **Pilar 1 (domínio próprio + HTTPS)** já está no ar em `https://cookalaroulette.com`
(DNS na Hostgator OK, GitHub Pages Custom Domain ativo, Enforce HTTPS ativo, 3 redirects 301
validados, arquivo `CNAME` no repo). Estas tasks cobrem o **Pilar 2 (SEO + analytics)** e os
ajustes finais do Pilar 1 (URLs absolutas pendentes). Todas as alterações são aditivas no
`<head>` + 1 linha JS + 2 arquivos novos. `<body>` permanece intacto (Princípio I).

**Convenção:** tarefas marcadas com **🧑** são ações operacionais do Felipe (fora do código, no
navegador/CLI). As demais são edições de arquivo.

## Phase 1: Setup (ações operacionais externas)

Estas tasks geram tokens/dados que vão ser usados depois nas tasks de código. Podem ser feitas
em paralelo entre si (são serviços diferentes).

- [ ] T001 🧑 [P] Criar conta no GoatCounter (https://www.goatcounter.com/signup) com slug **`cookalaroulette`** → painel ficará em `https://cookalaroulette.goatcounter.com`; confirmar e-mail; em Settings → Allowed hosts adicionar `cookalaroulette.com` e `localhost`
- [ ] T002 🧑 [P] No Google Search Console (https://search.google.com/search-console): Add property → **URL prefix** → `https://cookalaroulette.com/` → escolher método **HTML tag** → **COPIAR o token** (`google-site-verification` value) — NÃO clicar em "Verify" ainda (precisa do token estar deployado primeiro)

## Phase 2: Foundational

- [X] T003 Reconfirmar Pilar 1 antes de prosseguir: rodar `curl -sI https://cookalaroulette.com | head -3` (esperado HTTP/2 200) e `dig +short cookalaroulette.com` (esperado os 4 IPs do GitHub) — registrar print/saída no commit se algo divergir

## Phase 3: User Story 1 — Domínio próprio (Priority: P1)

**Goal**: completar a transição visual/social para o domínio novo — as URLs absolutas em OG/Twitter ainda apontam para o `.github.io`.
**Independent Test**: depois desta fase, compartilhar o link em uma rede social (ou usar o Facebook Debugger) mostra a prévia carregando `og:image` de `cookalaroulette.com`, não do `.github.io`.

- [X] T004 [US1] Atualizar URLs absolutas em `index.html` `<head>`: `og:url`, `og:image`, `twitter:image` → `https://cookalaroulette.com/...` (substituir o host `felipekanarek.github.io/cookalaroulette` por `cookalaroulette.com`). Textos OG/Twitter continuam por ora (US2 cuida disso).

**Checkpoint US1**: domínio próprio + HTTPS + redirects + URLs OG corretas. Compartilhamento social funciona com o domínio novo.

## Phase 4: User Story 2 — Encontrável no Google (Priority: P1)

**Goal**: o conjunto de mudanças de SEO + analytics — `<title>`/`<meta>` em EN, canonical, JSON-LD, OG/Twitter em EN, GSC verification, GoatCounter, `robots.txt`, `sitemap.xml`, e cadastros nos serviços externos.
**Independent Test**: depois desta fase, Lighthouse SEO ≥ 90; Google Rich Results Test passa o `WebSite`; `curl` mostra title/canonical/robots/sitemap; GoatCounter recebe visitas e eventos; Search Console verifica a propriedade e aceita o sitemap.

### Bloco A — alterações no `<head>` de `index.html` (sequenciais, mesmo arquivo)

- [X] T005 [US2] Substituir `<title>` em `index.html` por: `Cook à la Roulette — what should I cook today?`
- [X] T006 [US2] Substituir `<meta name="description">` em `index.html` pelo texto EN do contrato (`contracts/seo-meta.md` §1): "A typographic recipe roulette. Click and the universe decides what you'll cook today — random recipes from chefs around the world, redirecting to their original sites. Sorteador de receitas."
- [X] T007 [US2] Adicionar `<link rel="canonical" href="https://cookalaroulette.com/">` em `index.html` logo após `<meta name="description">`
- [X] T008 [US2] Adicionar `<meta name="google-site-verification" content="REPLACE_WITH_GSC_TOKEN">` em `index.html` (token real entra em T015 depois que Felipe abrir o GSC)
- [X] T009 [US2] Atualizar textos das tags Open Graph e Twitter em `index.html` para EN (espelhando title/description novos); manter URLs absolutas já corrigidas em T004
- [X] T010 [US2] Adicionar `<meta property="og:locale" content="en_US">` em `index.html` (no bloco OG)
- [X] T011 [US2] Adicionar bloco `<script type="application/ld+json">` em `index.html` com Schema.org `WebSite` (estrutura exata em `contracts/seo-meta.md` §5)
- [X] T012 [US2] Adicionar snippet do GoatCounter ao final do `<head>` de `index.html`: `<script data-goatcounter="https://cookalaroulette.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>` (precedido por comentário explicativo)

### Bloco B — arquivos paralelos (entre si e com Bloco A)

- [X] T013 [P] [US2] Criar `robots.txt` na raiz do repo com 3 linhas exatas (`contracts/robots.md`): `User-agent: *` / `Allow: /` / linha em branco / `Sitemap: https://cookalaroulette.com/sitemap.xml`
- [X] T014 [P] [US2] Criar `sitemap.xml` na raiz do repo com 1 `<url>` apontando para `https://cookalaroulette.com/` + `<lastmod>` data de hoje (`contracts/sitemap.md`)
- [X] T015 [P] [US2] Adicionar 1 linha em `app.js` dentro de `aoClicar()` (antes do `redirecionar(...)`): `try { window.goatcounter && window.goatcounter.count({ event: true, path: 'roleta-clique' }); } catch (_) {}`

### Bloco C — primeiro deploy

- [X] T016 [US2] Commit dos blocos A + B (mensagem: "feat(seo): meta SEO em EN + JSON-LD + GoatCounter + robots/sitemap"); push para origin/006-dominio-seo
- [ ] T017 [US2] Merge da branch `006-dominio-seo` em `main` (`git checkout main && git merge --no-ff 006-dominio-seo`) e `git push origin main` — GitHub Pages republica em ~30s

### Bloco D — validações pós-deploy

- [ ] T018 [US2] Aguardar Pages republicar e rodar validações automáticas: `curl -s https://cookalaroulette.com | grep -E '<title>|canonical|google-site-verification|application/ld\+json|goatcounter'` (todas devem aparecer); `curl -s https://cookalaroulette.com/robots.txt` (3 linhas); `curl -s https://cookalaroulette.com/sitemap.xml` (XML válido); `curl -sI https://cookalaroulette.com/assets/og-image.png` (200)
- [ ] T019 [US2] Validar JSON-LD em https://search.google.com/test/rich-results com URL `https://cookalaroulette.com/` — esperado: `WebSite` detectado, sem erros
- [ ] T020 [US2] Rodar Lighthouse SEO (https://pagespeed.web.dev/?url=https%3A%2F%2Fcookalaroulette.com%2F) e verificar score SEO ≥ 90 (SC-005); registrar no commit ou em `cobertura.md` se houver desvio
- [ ] T021 [US2] Forçar re-scrape dos previews sociais: Facebook Debugger (https://developers.facebook.com/tools/debug/?q=https%3A%2F%2Fcookalaroulette.com%2F) → "Scrape Again"; Twitter Card Validator (https://cards-dev.twitter.com/validator) — esperar imagem 1200×630 + textos EN

### Bloco E — completar Search Console (depende do deploy)

- [ ] T022 🧑 [US2] No GSC (`https://cookalaroulette.com/`): clicar **Verify** — esperado: "Ownership verified". Se falhar, conferir que o `<meta name="google-site-verification">` está com o token correto em `index.html` (não o placeholder)
- [ ] T023 [US2] Atualizar `index.html`: substituir `REPLACE_WITH_GSC_TOKEN` pelo token real copiado em T002; commitar e fazer push direto na `main` (single-line change) — repete o deploy do Pages
- [ ] T024 🧑 [US2] No GSC: aba **Sitemaps** → adicionar `sitemap.xml` → submit; esperado status "Success" (pode demorar minutos)
- [ ] T025 🧑 [US2] Confirmar no painel do GoatCounter (`https://cookalaroulette.goatcounter.com`) que há **≥ 1 visita** registrada e que clicar no site real dispara um **evento `roleta-clique`** (SC-008)

**Nota importante sobre a ordem T022/T023**: a sequência real é T023 PRIMEIRO (colocar o token real) → push → esperar Pages republicar → T022 (verificar no GSC). As tasks ficaram nessa ordem porque T022 também pode ser tentada com o placeholder e vai falhar, sinalizando a necessidade de T023. Para reduzir fricção, **executar T023 antes de T022** quando chegar nesse ponto.

**Checkpoint US2**: SEO + analytics no ar; Search Console verificado e com sitemap; GoatCounter contando.

## Phase 5: User Story 3 — Tela continua minimalista (Priority: P1, invariante)

**Goal**: validar que nada visível mudou na tela.
**Independent Test**: comparação visual + DevTools.

- [ ] T026 [US3] Abrir `https://cookalaroulette.com` em aba anônima: verificar visualmente que a tela é a mesma (texto-marca COOK / À LA / ROULETTE, laranja sobre off-white). Inspecionar `<body>` no DevTools → confirmar que NÃO existem elementos novos visíveis (sem banners, badges, widgets). Inspecionar Application → Cookies → confirmar **0 cookies** (SC-006).

## Phase 6: Polish & Cross-Cutting

- [ ] T027 [P] Atualizar `README.md`: trocar todas as referências de `felipekanarek.github.io/cookalaroulette` por `cookalaroulette.com`; adicionar marcador "Fase 6 ✅" na lista de fases; nota sobre o GoatCounter como exceção documentada
- [ ] T028 [P] Atualizar metadados do repo: `gh repo edit felipekanarek/cookalaroulette --homepage https://cookalaroulette.com` (a descrição pode permanecer ou ganhar menção EN)
- [ ] T029 [P] Atualizar memória do projeto (`~/.claude/projects/-Users-infoprice-cookAlaRoulette/memory/cookalaroulette-status.md`): registrar Fase 6 ✅ no ar em `cookalaroulette.com`, GoatCounter ativo
- [ ] T030 Commit final ("docs(006): README + memória + homepage do repo atualizados") + push; verificar que `git status` está limpo e que `git log --oneline -5` mostra a Fase 6 fechada
- [ ] T031 Validar todos os SCs da spec ao vivo (SC-001 a SC-008) e registrar resultados; SC-003/SC-004/SC-007 têm janelas de 30/60 dias — anotar a data inicial pra revisitar

## Dependencies & Execution

- **T001 + T002** (manuais) **devem começar primeiro** — geram dados necessários (slug, token).
- **T003** confirma o estado do Pilar 1 antes de qualquer alteração.
- **T004** (US1) é independente das US2 — pode ir junto no commit das US2 ou separado.
- **Bloco A (T005-T012)** é sequencial (mesmo arquivo `index.html`).
- **Bloco B (T013-T015)** é totalmente paralelo (arquivos diferentes).
- **Bloco C (T016-T017)** depende de A + B completos.
- **Bloco D (T018-T021)** depende de C (precisa estar no ar).
- **Bloco E (T022-T025)** depende de D + T002 (token disponível) — note a ordem prática T023 antes de T022.
- **Phase 5 (T026)** depende de US2 estar deployada (precisa do canonical/JSON-LD ativos para o teste ser real).
- **Polish (T027-T031)** é o fechamento.

### Exemplo de paralelização

- T001 e T002 podem ser feitas em duas abas do navegador simultaneamente.
- T013, T014 e T015 podem ser editadas em paralelo (arquivos distintos) entre os passos do Bloco A.
- T027, T028 e T029 são todos polish em arquivos/sistemas distintos — paralelos.

## Implementation Strategy

- **MVP da fase**: Bloco A + B + C — depois disso a homepage já tem SEO básico no ar e
  o GoatCounter já começa a contar (mesmo sem GSC verificado ainda).
- **Entrega incremental**: 2 deploys — primeiro o bloco principal (Bloco C), depois o
  token GSC real (T023).
- **Risco mais baixo**: tudo é aditivo. Se algo der ruim, `git revert` do commit do
  Bloco C devolve a homepage ao estado pré-SEO (mantendo o domínio + HTTPS funcionando).

## Resumo

- **Total**: 31 tarefas. **US1**: 1 (T004). **US2**: 21 (T005-T025). **US3**: 1 (T026).
  Setup/Foundational: 3 (T001-T003). Polish: 5 (T027-T031).
- **Ações manuais 🧑**: 5 (T001, T002, T022, T024, T025).
- **Paralelizáveis [P]**: 6 (T001/T002 entre si; T013/T014/T015 entre si; T027/T028/T029 entre si).
- **MVP sugerido**: T001 + T002 + T003 + T004 + T005-T017 (até o deploy do Bloco C — já tem SEO no ar).
