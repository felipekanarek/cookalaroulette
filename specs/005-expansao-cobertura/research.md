# Research — Expansão de Cobertura (Lista 2)

Consolidação das decisões técnicas. A escolha final de técnica de cada site é confirmada na
**sondagem** (parte da implementação), mas aqui fixamos a estratégia por categoria e o protocolo.

## Decisão 1 — Técnica por categoria de site

**Decisão:** classificar cada site numa de quatro trilhas e aplicar a técnica correspondente,
sempre tentando a mais simples primeiro (ordem da constituição: sitemap → BeautifulSoup → Playwright).

| Trilha | Sites (dica da Lista 2) | Técnica inicial |
|--------|--------------------------|-----------------|
| A. Blog WordPress/sitemap limpo | maioria dos chefs individuais (food blogs US/EU, ex.: Sally's Baking, Pinch of Yum, Love and Lemons, Downshiftology, Minimalist Baker, Gimme Some Oven, Joy the Baker, Leite's Culinaria, Chopstick Chronicles, Korean Bapsang, Archana's Kitchen, African Bites, Two Spoons, Cravings Journal, My Colombian Recipes, Chilean Food & Garden, etc.) | `coletar_por_sitemap` + filtro `_e_receita` |
| B. Editorial/marca grande | Great British/Italian/Spanish/Polish Chefs, GialloZafferano, King Arthur, Saveur, The Kitchn, Hogarmania | `coletar_por_sitemap` (sub-filtro p/ seção de receitas) ou listagem; alguns podem exigir navegador |
| C. Requer navegador (JS) | Ranveer Brar, Ken Hom, Damn Delicious, Food52, Mexico in My Kitchen | `coletar_por_sitemap_browser` ou `coletar_por_listagem(usar_browser=True)` |
| D. Bloqueado na verificação (Cloudflare/WAF), acessível via Python | BBC Good Food, Bon Appétit, Epicurious, Food & Wine, Martha Stewart, Delish, The Spruce Eats | `coletar_por_sitemap` por HTTP (UA navegador); se totalmente bloqueado → `coletar_por_wayback` |

**Rationale:** reaproveita as 5 técnicas já provadas nas Fases 2/3; a trilha é só um ponto de
partida — a sondagem decide. **Alternativas rejeitadas:** escrever um coletor genérico único (não
absorve a heterogeneidade dos sites); usar sempre navegador (lento e desnecessário para sitemaps).

## Decisão 2 — Protocolo de sondagem por site (antes de escrever o adaptador)

**Decisão:** para cada site, rodar nesta ordem e escolher a primeira que entrega receitas reais:

```bash
curl -sI https://SITE/sitemap.xml | head -3          # existe? 200/403/404?
curl -s  https://SITE/robots.txt | grep -i sitemap   # localização do(s) sitemap(s)
curl -sI https://SITE/recipes/ | head -3             # tem página de listagem?
# se sitemap 403/JS → testar coletar_por_sitemap_browser
# se nada → testar crawl/listagem; se Cloudflare total → wayback (CDX do Internet Archive)
```

Validação de aceite do adaptador: `coletar(10)` retorna ≥1 registro com URL de receita real e
viva. Filtro `_e_receita` calibrado para excluir não-receitas (categorias, autor, institucional,
mídia, taxonomia) — o trabalho principal de cada adaptador.

**Rationale:** mesmo método que levou de 6→31 chefs; barato e determinístico.

## Decisão 3 — Campo `chef` para marcas/editoriais e coquetéis

**Decisão (clarificada):** usar o **nome da marca** no campo `chef` (ex.: "GialloZafferano",
"The Kitchn", "Great British Chefs", "Liquor.com", "Punch", "Difford's Guide"). Coquetéis entram
no mesmo catálogo/contrato. Para chefs individuais, usar o nome da pessoa (como na Lista 1).

**Rationale:** consistente com "The Woks of Life" (marca) já presente; o sorteio em duas etapas
(chef → receita) trata a marca como um "chef" sem qualquer mudança de código.
**Alternativa rejeitada:** caçar um editor/pessoa por site editorial — trabalho extra sem ganho.

## Decisão 4 — Sites "bloqueados na verificação" e `url_viva`

**Decisão:** confiar na política existente de `url_viva` (orquestrador): 2xx OU 401/403/429 =
página existe (viva), pois o app redireciona um humano. Coleta por HTTP com User-Agent de
navegador quando o de bot for recusado. `coletar_por_wayback` só quando o site for totalmente
inacessível mesmo via navegador (Cloudflare hard).

**Rationale:** já validado na Fase 3 (kwestiasmaku, Serious Eats); legítimo (não evade proteção).

## Decisão 5 — Integração incremental por lotes + prestação de contas

**Decisão:** implementar em **lotes de ~8–10 sites** com sub-agentes paralelos (1 por site);
após cada lote, registrar os adaptadores no orquestrador e integrar via
`python3 orquestrador.py --site <m1> --site <m2> ... --limite N` (mescla, preserva Lista 1).
Documentar em cada lote: integrados (contagem), sem-receitas, bloqueados, mortos — com motivo.

**Rationale:** o modo `--site` (criado nesta sessão) evita re-raspar os 30+ existentes; lotes
mantêm o trabalho gerenciável e reversível por site; falha isolada não derruba o lote (FR-014).
**Alternativa rejeitada:** uma única rodada completa gigante — lenta, frágil e tudo-ou-nada.

## Decisão 6 — Teto de coleta por site nesta fase

**Decisão:** durante a validação, `--limite 10–25` (rápido). Na integração, teto moderado por
técnica (ex.: 500–2000 para sitemap; crawl plateia sozinho). Evitar tetos enormes que inflam o
`receitas.json` (payload do frontend) sem ganho proporcional de variedade.

**Rationale:** equilíbrio cobertura × tamanho do payload (já discutido: ~0,8 MB gzip hoje).

## Riscos / pontos de atenção

- **Sites de coquetéis** podem ter estrutura de URL distinta (ex.: `/recipe/` vs slug-raiz) — filtro dedicado.
- **Condé Nast / Dotdash / Hearst** (Bon Appétit, Epicurious, Food & Wine, Delish, Spruce Eats, Martha Stewart): WAF agressivo; provável trilha D (sitemap via HTTP + url_viva tolerante, ou wayback).
- **Food52** é editorial + comunidade (volume alto e ruidoso) — filtro restritivo + teto moderado.
- **Tamanho do catálogo**: monitorar `receitas.json` gzip a cada lote; se crescer demais, reduzir tetos.
- **Sobreposição com Lista 1**: nenhum site repetido; dedup por URL do orquestrador protege.
