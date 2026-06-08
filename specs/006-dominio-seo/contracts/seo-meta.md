# Contrato — Elementos SEO do `<head>`

Contrato dos elementos a serem adicionados/atualizados em `index.html` na Fase 6. Tudo entra
no `<head>`; `<body>` permanece inalterado.

## Ordem sugerida no `<head>` (depois do `<meta viewport>`)

1. SEO básico (title, description, canonical)
2. Verificação Google Search Console
3. Open Graph (atualizado)
4. Twitter Cards (atualizado)
5. JSON-LD Schema.org
6. Recursos visuais (favicon, stylesheet — já existem)
7. GoatCounter (no fim, async)

## 1. SEO básico

```html
<title>Cook à la Roulette — what should I cook today?</title>
<meta name="description" content="A typographic recipe roulette. Click and the universe decides what you'll cook today — random recipes from chefs around the world, redirecting to their original sites. Sorteador de receitas.">
<link rel="canonical" href="https://cookalaroulette.com/">
```

Regras:
- `<title>` ≤ 70 caracteres (display do Google).
- `<meta description>` ~155-160 caracteres.
- `<link rel="canonical">` MUST apontar para o apex HTTPS exato (`https://cookalaroulette.com/`).

## 2. Verificação Google Search Console

```html
<meta name="google-site-verification" content="REPLACE_WITH_GSC_TOKEN">
```

Regras:
- O `content="..."` será preenchido depois que Felipe abrir o Search Console e adicionar a
  propriedade `cookalaroulette.com` — o GSC gera o token.
- Inicialmente entra como **placeholder explícito** (`REPLACE_WITH_GSC_TOKEN`) para sinalizar
  que falta o passo manual; o quickstart documenta como completar.
- Uma vez verificado, a tag pode permanecer (boa prática) — o GSC mantém a posse.

## 3. Open Graph (URLs atualizadas para o domínio novo, textos em EN)

```html
<meta property="og:type"          content="website">
<meta property="og:title"         content="Cook à la Roulette — what should I cook today?">
<meta property="og:description"   content="A typographic recipe roulette. Click and the universe decides what you'll cook today.">
<meta property="og:url"           content="https://cookalaroulette.com/">
<meta property="og:image"         content="https://cookalaroulette.com/assets/og-image.png">
<meta property="og:image:width"   content="1200">
<meta property="og:image:height"  content="630">
<meta property="og:locale"        content="en_US">
```

## 4. Twitter Cards

```html
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="Cook à la Roulette — what should I cook today?">
<meta name="twitter:description" content="A typographic recipe roulette. Click and the universe decides what you'll cook today.">
<meta name="twitter:image"       content="https://cookalaroulette.com/assets/og-image.png">
```

## 5. JSON-LD Schema.org

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Cook à la Roulette",
  "alternateName": "COOK À LA ROULETTE",
  "url": "https://cookalaroulette.com/",
  "description": "A typographic recipe roulette. Click and the universe decides what you'll cook today — random recipes from chefs around the world.",
  "inLanguage": "en",
  "author": {
    "@type": "Person",
    "name": "Felipe Kanarek",
    "url": "https://github.com/felipekanarek"
  },
  "license": "https://github.com/felipekanarek/cookalaroulette/blob/main/LICENSE"
}
</script>
```

Regras:
- Validar em https://search.google.com/test/rich-results após deploy — deve passar sem erros.

## 6. GoatCounter (no fim do `<head>`)

```html
<!-- Analytics privacy-friendly: sem cookies, sem dados pessoais, sem banner. -->
<script data-goatcounter="https://cookalaroulette.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>
```

Regras:
- `async` obrigatório — não pode bloquear render.
- Falha-silenciosa: se o script não carregar (ad-blocker, offline), o produto segue funcionando.
- O slug `cookalaroulette` (subdomínio do painel) é definido por Felipe ao criar a conta. Se for
  outro, ajustar a URL acima.

## Critério de aceite

1. `curl -s https://cookalaroulette.com | grep '<title>'` retorna o título EN correto.
2. `curl -s https://cookalaroulette.com | grep 'canonical'` retorna o canonical pro apex.
3. Validador Rich Results do Google passa o JSON-LD `WebSite`.
4. Facebook Debugger (https://developers.facebook.com/tools/debug/) renderiza a prévia OG com
   imagem 1200×630 e textos EN.
5. Twitter Card Validator faz o mesmo.
6. Lighthouse SEO ≥ 90.
7. Após Felipe abrir o painel do GoatCounter, vê visitas + eventos `roleta-clique`.
