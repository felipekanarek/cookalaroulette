# Research — Domínio próprio + SEO (Fase 6)

Decisões técnicas finas que sustentam o plano. Decisões maiores (escopo, idioma, analytics)
foram resolvidas no `/speckit-clarify` e estão na Sessão 2026-06-08 da spec.

## Decisão 1 — Texto do `<title>` e da `<meta description>` (em inglês)

**Decisão:**

```html
<title>Cook à la Roulette — what should I cook today?</title>
<meta name="description" content="A typographic recipe roulette. Click and the universe decides what you'll cook today — random recipes from chefs around the world, redirecting to their original sites. Sorteador de receitas.">
```

**Rationale:** o `<title>` casa a marca + a query de intenção (~50-60 caracteres, dentro do
ideal de display do Google). A `<meta description>` (~155-160 chars) explica o produto em 1
frase, menciona o termo PT secundário ("sorteador de receitas") para captura em buscas
brasileiras, e reforça o redirect (Princípio III — não somos agregador).

**Alternativas rejeitadas:** title só com a marca ("Cook à la Roulette") — perde a query de
intenção; title só em pt-BR ("Sorteador de receitas — Cook à la Roulette") — contraria a
clarificação de EN como idioma principal e o catálogo majoritariamente inglês.

## Decisão 2 — Formato do JSON-LD Schema.org

**Decisão:** tipo `WebSite` simples no `<head>`, sem `SearchAction` (não temos página de busca).

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

**Rationale:** `WebSite` é o mínimo que sinaliza "isto é um produto coerente, não um lixo".
`author` ajuda o Google a entender autoria. `license` aponta a MIT (já existe no repo).
`inLanguage: "en"` casa com a decisão de SEO em EN; **não conflita** com `lang="pt-BR"` da página
(um descreve o conteúdo na ótica de busca; outro, a língua de leitura/acessibilidade).

**Alternativas rejeitadas:**
- `WebSite` com `SearchAction` (caixa de busca no Google) — não temos endpoint de busca; mentiria.
- `WebApplication` — exigiria `applicationCategory`, `offers`, etc. e o produto não é um app
  com features descritíveis; é uma roleta clicável.
- JSON-LD múltiplos (`Organization` + `WebSite` + `Person`) — overkill para 1 página.

## Decisão 3 — `<link rel="canonical">`

**Decisão:** `<link rel="canonical" href="https://cookalaroulette.com/">` no `<head>`.

**Rationale:** sinal explícito ao Google de que o domínio próprio é a versão canônica, mesmo
que o `.github.io` antigo ainda exista (com redirect 301). Reforça a consolidação de autoridade.

**Alternativas rejeitadas:** omitir o canonical e confiar só no redirect 301 — funciona, mas
o canonical é o padrão da indústria e duplica o sinal sem custo.

## Decisão 4 — Atualizar Open Graph e Twitter para o novo domínio

**Decisão:** trocar todas as 3 URLs absolutas em `<meta>` OG/Twitter:

```html
<meta property="og:url"     content="https://cookalaroulette.com/">
<meta property="og:image"   content="https://cookalaroulette.com/assets/og-image.png">
<meta name="twitter:image"  content="https://cookalaroulette.com/assets/og-image.png">
```

E o texto de `og:title`/`og:description`/`twitter:*` em inglês alinhado ao `<title>`/`<meta
description>` da decisão 1.

**Rationale:** previews sociais (WhatsApp, Twitter, LinkedIn) usam essas URLs absolutas. Sem
isso, o link continua mostrando `og:image` carregando do `.github.io` (que vai 301-ar, mas
muitos scrapers de preview não seguem redirect — quebra a imagem).

## Decisão 5 — Método de verificação no Google Search Console

**Decisão:** **meta tag** `<meta name="google-site-verification" content="...">` no `<head>`.

**Rationale:** mais simples que TXT no DNS — não exige voltar no painel Hostgator. Uma vez
adicionado e re-deployado, o GSC valida em 5 min. A meta pode ser removida depois de validar
(o GSC mantém a propriedade), mas é convencional deixar.

**Alternativas rejeitadas:**
- TXT DNS record — funciona, mas exige outra ida ao painel da Hostgator e nova propagação.
- Upload de arquivo HTML — também funciona, mas polui a raiz do repo com um arquivo opaco.

**Nota operacional:** o valor real do `content="..."` só está disponível depois que o
mantenedor (Felipe) abrir o Search Console e adicionar a propriedade `cookalaroulette.com`. O
fluxo é: implementar a meta com placeholder → Felipe cola o valor real → re-commit → GSC
valida. Documentado no `quickstart.md` e nas tasks.

## Decisão 6 — Setup do GoatCounter

**Decisão:** conta gratuita do GoatCounter com slug **`cookalaroulette`** (gera o painel em
`https://cookalaroulette.goatcounter.com`). Snippet no final do `<head>`:

```html
<script data-goatcounter="https://cookalaroulette.goatcounter.com/count"
        async src="//gc.zgo.at/count.js"></script>
```

E no `app.js`, dentro do `aoClicar()`, antes do `redirecionar(...)`:

```javascript
// Analytics privacy-friendly (best-effort, falha silenciosa)
try { window.goatcounter && window.goatcounter.count({ event: true, path: 'roleta-clique' }); } catch (_) {}
```

**Rationale:** o GoatCounter usa `data-goatcounter` no próprio `<script>`, sem necessidade de
config global JS. `async` evita bloquear render. O `try/catch` blinda contra qualquer falha
(p.ex. ad-blocker que remove o script) — o sorteio continua funcionando sempre.

**Setup manual (Felipe faz uma vez):**
1. Criar conta em https://www.goatcounter.com/signup
2. Escolher slug `cookalaroulette` (ou ajustar a constante no script se outro)
3. Site code = `cookalaroulette` → painel em `https://cookalaroulette.goatcounter.com`
4. (Opcional) Em Settings → Allowed hosts: adicionar `cookalaroulette.com` (e `localhost` para teste)

**Alternativas rejeitadas:** mesmo argumento da spec (Plausible pago, Cloudflare sem evento
custom, self-host com fricção operacional, Google Analytics com cookies/banner).

## Decisão 7 — Conteúdo do `robots.txt`

**Decisão:**

```
User-agent: *
Allow: /

Sitemap: https://cookalaroulette.com/sitemap.xml
```

**Rationale:** o mínimo necessário — permite tudo (não há área administrativa a esconder) e
aponta o sitemap. Não desbloqueamos `Disallow` explícito do `.git/` etc. porque o Pages já
não serve esses arquivos.

## Decisão 8 — Conteúdo do `sitemap.xml`

**Decisão:** 1 entry, a homepage canônica.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://cookalaroulette.com/</loc>
    <lastmod>2026-06-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

**Rationale:** o produto é uma única tela. **Não** listamos as URLs das receitas (cada uma é
de um chef terceiro; sitemap de terceiros já existe; o nosso job é redirecionar). Atualizar
`<lastmod>` quando re-deployar é trivial — pode ficar manual por ora.

**Alternativa rejeitada:** sitemap dinâmico/script gerado por build — overkill para 1 URL.

## Riscos / pontos de atenção

- **`og-image.png` 404 no domínio novo até o deploy:** atualmente o arquivo está em
  `assets/og-image.png` (mesmo path); só muda o host na URL absoluta. Confirmar com
  `curl -I https://cookalaroulette.com/assets/og-image.png` depois do deploy (esperar 200).
- **Cache dos previews sociais:** WhatsApp/Twitter cacheiam OG image por dias. Forçar
  re-scrape em https://developers.facebook.com/tools/debug/ e https://cards-dev.twitter.com/validator
  depois do deploy ajuda.
- **GSC pode demorar a indexar:** SC-003/SC-004 têm janela de 30 dias justamente por isso.
  Submeter o sitemap **imediatamente** depois de verificar a propriedade reduz o tempo.
- **GoatCounter ad-blockers:** alguns ad-blockers removem `gc.zgo.at`. O `try/catch` blinda.
  Métrica será sub-contada, mas seguirá sendo útil como tendência.

## Resumo das decisões

| # | Decisão | Onde aparece no código |
|---|---------|------------------------|
| 1 | Title + Meta description em EN | `index.html` `<head>` |
| 2 | JSON-LD `WebSite` simples | `index.html` `<head>` |
| 3 | Canonical pro apex HTTPS | `index.html` `<head>` |
| 4 | OG/Twitter URLs pro domínio novo | `index.html` `<head>` |
| 5 | Verificação GSC via meta tag | `index.html` `<head>` (placeholder + valor real depois) |
| 6 | GoatCounter slug `cookalaroulette` + evento `roleta-clique` | `index.html` `<head>` + `app.js` `aoClicar` |
| 7 | `robots.txt` mínimo + sitemap link | `/robots.txt` (novo) |
| 8 | `sitemap.xml` com 1 URL | `/sitemap.xml` (novo) |
