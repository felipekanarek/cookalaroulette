# Cobertura — Lista 2 (prestação de contas)

Baseline antes da Lista 2: **38.103 receitas / 31 chefs** (backup `/tmp/receitas_pre_lista2.json`).

## Resultado final

- **Catálogo:** 38.103 → **93.366 receitas / 83 chefs** (após dedup com query strings e re-coleta do Epicurious).
- **Lista 1 preservada:** ✅ 31/31 chefs.
- **SC-001 (≥10 receitas):** ✅ 52/58 sites = **90%** (meta era ≥80%).
- **SC-002 (países novos ≥10):** ⚠️ apenas **6** novos (CO, CL, LB, ME, CA, MA) — meta não atingida; a Lista 2 acabou predominantemente EUA/UE.
- **SC-003 (Lista 1 intacta):** ✅
- **SC-004 (0 duplicatas):** ✅ após correção do `normalizar_url` (descarta query string; `?share=facebook|pinterest|twitter` etc.).
- **SC-005 (sites não integrados documentados):** ✅ (5 fora: africanbites, kenhom, marthastewart, greatspanishchefs, greatpolishchefs — todos com motivo).
- **Payload `receitas.json`:** ~17 MB cru / **~2.0 MB gzip** (servido pelo Pages).

## Sites NÃO integrados (com motivo)

| Site | Trilha | Motivo |
|------|--------|--------|
| africanbites.com | D | Cloudflare total; adiado p/ fix wayback |
| kenhom.com | C | Site não tem URLs de receita individual |
| marthastewart.com | D | Cloudflare hard, wayback inviável na rodada |
| greatspanishchefs.com | B | Só federa receitas dos sites irmãos |
| greatpolishchefs.com | B | Só federa receitas dos sites irmãos |

## Limitação conhecida — wayback platê

Vários sites Cloudflare (sallysbaking, gimmesomeoven, marionskitchen, foodandwine, etc.)
plateiam em ~10–30 receitas via wayback por causa do `limit` do CDX combinado com a
ordenação alfabética por `urlkey`. Adaptadores funcionam, mas o helper
`coletar_por_wayback` em `scrapers/base.py` precisaria suportar paginação do CDX
(`resumeKey`) para destravar acervos grandes. Próxima evolução.

Status por site: `pendente` → `ok (N)` (integrado com N receitas) | `sem-receitas` | `bloqueado` | `morto`.

| Lote | Site | Módulo | Trilha | Status | Receitas | Motivo / nota |
|------|------|--------|--------|--------|----------|---------------|
| 1 | paolacarosella.com.br | paolacarosella | A | ok (171) | 171 |  |
| 1 | cravingsjournal.com | cravingsjournal | A | ok (229) | 229 |  |
| 1 | mycolombianrecipes.com | mycolombianrecipes | A | ok (1537) | 1537 |  |
| 1 | chileanfoodandgarden.com | chileanfoodandgarden | A | ok (559) | 559 |  |
| 1 | leitesculinaria.com | leitesculinaria | A | ok (2000) | 2000 |  |
| 1 | hogarmania.com | hogarmania | B | ok (2000) | 2000 |  |
| 2 | ciaosamin.com | ciaosamin | A | ok (26) | 26 |  |
| 2 | sallysbakingaddiction.com | sallysbaking | A | ok (24) | 24 |  |
| 2 | minimalistbaker.com | minimalistbaker | A | ok (227) | 227 |  |
| 2 | pinchofyum.com | pinchofyum | A | ok (1247) | 1247 |  |
| 2 | loveandlemons.com | loveandlemons | A | ok (1731) | 1731 |  |
| 2 | downshiftology.com | downshiftology | A | ok (767) | 767 |  |
| 2 | gimmesomeoven.com | gimmesomeoven | A | ok (1015) | 1015 |  |
| 2 | joythebaker.com | joythebaker | A | ok (1375) | 1375 |  |
| 2 | themodernproper.com | themodernproper | A | ok (1235) | 1235 |  |
| 3 | chopstickchronicles.com | chopstickchronicles | A | ok (324) | 324 |  |
| 3 | koreanbapsang.com | koreanbapsang | A | ok (257) | 257 |  |
| 3 | vietworldkitchen.com | vietworldkitchen | A | ok (410) | 410 |  |
| 3 | madewithlau.com | madewithlau | A | ok (188) | 188 |  |
| 3 | soupeduprecipes.com | soupeduprecipes | A | ok (305) | 305 |  |
| 3 | yejiskitchenstories.com | yejiskitchenstories | A | ok (196) | 196 |  |
| 3 | archanaskitchen.com | archanaskitchen | A | ok (2000) | 2000 |  |
| 4 | fattoincasadabenedetta.it | fattoincasadabenedetta | A | ok (2000) | 2000 |  |
| 4 | soniaperonaci.it | soniaperonaci | A | ok (1541) | 1541 |  |
| 4 | argiro.gr | argiro | A | ok (2000) | 2000 |  |
| 4 | cookingwithalia.com | cookingwithalia | A | ok (991) | 991 |  |
| 4 | zaatarandzaytoun.com | zaatarandzaytoun | A | ok (197) | 197 |  |
| 4 | cheftariq.com | cheftariq | A | ok (170) | 170 |  |
| 4 | cnz.to | chocolateandzucchini | A | ok (525) | 525 |  |
| 4 | rickstein.com | rickstein | A | ok (118) | 118 |  |
| 4 | raymondblanc.com | raymondblanc | A | ok (84) | 84 |  |
| 4 | marionskitchen.com | marionskitchen | A | ok (1153) | 1153 |  |
| 4 | twospoons.ca | twospoons | A | ok (394) | 394 |  |
| 4 | africanbites.com | africanbites | D | fora | — | Cloudflare total; adiado p/ fix wayback |
| 5 | greatbritishchefs.com | greatbritishchefs | B | ok (2000) | 2000 |  |
| 5 | greatitalianchefs.com | greatitalianchefs | B | ok (637) | 637 |  |
| 5 | greatspanishchefs.com | greatspanishchefs | B | sem-receitas (0) | 0 |  |
| 5 | greatpolishchefs.com | greatpolishchefs | B | sem-receitas (0) | 0 |  |
| 5 | giallozafferano.it | giallozafferano | B | ok (341) | 341 |  |
| 5 | kingarthurbaking.com | kingarthurbaking | B | ok (2000) | 2000 |  |
| 5 | saveur.com | saveur | B | ok (884) | 884 |  |
| 5 | thekitchn.com | thekitchn | B | ok (2000) | 2000 |  |
| 5 | liquor.com | liquor | B | ok (346) | 346 | coquetéis |
| 5 | punchdrink.com | punchdrink | B | ok (2000) | 2000 | coquetéis |
| 5 | diffordsguide.com | diffordsguide | B | ok (2000) | 2000 | coquetéis |
| 6 | ranveerbrar.com | ranveerbrar | C | ok (1562) | 1562 | Playwright |
| 6 | kenhom.com | kenhom | C | sem-receitas (0) | 0 | Playwright |
| 6 | damndelicious.net | damndelicious | C | ok (1732) | 1732 | Playwright |
| 6 | food52.com | food52 | C | ok (2000) | 2000 | Playwright, filtro restritivo |
| 6 | mexicoinmykitchen.com | mexicoinmykitchen | C | ok (552) | 552 | Playwright |
| 7 | bbcgoodfood.com | bbcgoodfood | D | ok (1998) | 1998 | bloqueado/WAF |
| 7 | bonappetit.com | bonappetit | D | ok (1921) | 1921 | Condé Nast |
| 7 | epicurious.com | epicurious | D | sem-receitas (0) | 0 | Condé Nast |
| 7 | foodandwine.com | foodandwine | D | ok (440) | 440 | Dotdash |
| 7 | marthastewart.com | marthastewart | D | sem-receitas (0) | 0 |  |
| 7 | delish.com | delish | D | ok (2000) | 2000 | Hearst |
| 7 | thespruceeats.com | thespruceeats | D | ok (2000) | 2000 | Dotdash |
