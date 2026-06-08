# Quickstart — Fase 6 (Domínio + SEO)

Passo a passo para executar e validar a Fase 6. Pré-requisito já cumprido: domínio
`cookalaroulette.com` está no ar com HTTPS (Pilar 1).

## Ações manuais do Felipe (uma vez, externas ao código)

### 1. Conta no GoatCounter

1. Abrir https://www.goatcounter.com/signup
2. Escolher slug **`cookalaroulette`** (vira o painel em `cookalaroulette.goatcounter.com`)
3. Confirmar e-mail
4. (opcional) Em Settings → Allowed hosts: adicionar `cookalaroulette.com` (e `localhost` se for testar localmente)

Pronto. O script do `<head>` já vai mandar dados pra cá assim que a fase for deployada.

### 2. Conta no Google Search Console

1. Abrir https://search.google.com/search-console
2. **Add property → URL prefix** → digitar `https://cookalaroulette.com/`
3. O GSC oferece vários métodos de verificação — escolher **HTML tag** (meta tag)
4. **Copiar o token** que aparece (algo tipo `abc123XYZ...`)
5. Aguardar — só verificar depois que a meta tag estiver deployada (passo abaixo)

## Implementação do código

Cada tarefa do `tasks.md` referencia este quickstart. Resumo do que muda:

### Arquivos a alterar

- `index.html` — `<head>` ganha title/description EN, canonical, JSON-LD, OG/Twitter atualizadas, meta GSC, script GoatCounter (ver `contracts/seo-meta.md`).
- `app.js` — `aoClicar()` ganha 1 linha disparando evento `roleta-clique` no GoatCounter.
- `README.md` — URLs apontam pro domínio novo + nota da Fase 6.

### Arquivos novos

- `robots.txt` (raiz) — ver `contracts/robots.md`.
- `sitemap.xml` (raiz) — ver `contracts/sitemap.md`.

### Comando final: atualizar repo metadata

```bash
gh repo edit felipekanarek/cookalaroulette --homepage https://cookalaroulette.com
```

## Validação (rodar depois do deploy)

```bash
# 1. Site responde no domínio novo
curl -sI https://cookalaroulette.com | head -3
# Esperado: HTTP/2 200

# 2. Título e canonical chegaram
curl -s https://cookalaroulette.com | grep -E '<title>|canonical'
# Esperado: title EN + canonical pro apex

# 3. robots.txt
curl -s https://cookalaroulette.com/robots.txt
# Esperado: 3 linhas (User-agent, Allow, Sitemap)

# 4. sitemap.xml
curl -s https://cookalaroulette.com/sitemap.xml | head
# Esperado: XML válido com 1 <url>

# 5. OG image responde no domínio novo
curl -sI https://cookalaroulette.com/assets/og-image.png | head -3
# Esperado: HTTP/2 200

# 6. JSON-LD válido
# Colar a homepage em https://search.google.com/test/rich-results
# Esperado: "WebSite" detectado, sem erros.

# 7. Lighthouse SEO
# Abrir https://pagespeed.web.dev/?url=https%3A%2F%2Fcookalaroulette.com%2F
# Esperado: SEO ≥ 90.

# 8. GoatCounter recebendo dados
# Abrir https://cookalaroulette.goatcounter.com → ver visitas e eventos.

# 9. Search Console verificado + sitemap submetido
# Em https://search.google.com/search-console → propriedade verificada;
# Sitemaps → adicionar "sitemap.xml" → "Submitted".
```

## Validação visual (Princípio I — invariante crítico)

1. Abrir https://cookalaroulette.com em aba anônima
2. Comparar com print da Fase 5 (mesma tela tipográfica COOK / À LA / ROULETTE)
3. Inspecionar `<body>` no DevTools — não há elementos novos
4. Inspecionar Application → Cookies — vazio
5. Clicar — deve sortear e redirecionar normalmente; depois verificar no painel do GoatCounter que o evento `roleta-clique` foi registrado

## Rollback (se algo der ruim)

A fase é puramente aditiva ao `<head>` + 1 linha JS + 2 arquivos novos. Para reverter:

```bash
git revert <commit-da-implementação>
git push
```

GitHub Pages volta ao estado anterior em ~30s. O domínio próprio continua funcionando — só o
SEO/analytics volta ao default da Fase 4.
