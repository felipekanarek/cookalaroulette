# Contrato — `robots.txt`

Arquivo de texto plano na **raiz do site**: `https://cookalaroulette.com/robots.txt`.

## Conteúdo exato

```
User-agent: *
Allow: /

Sitemap: https://cookalaroulette.com/sitemap.xml
```

## Regras

- Encoding: UTF-8 (ou ASCII; só caracteres latinos).
- Sem BOM.
- Sem regras `Disallow:` — o site é todo público. O catálogo `data/receitas.json` é estático e
  pode ser rastreado (não é confidencial; redireciona pra URLs públicas dos chefs).
- A linha `Sitemap:` ajuda crawlers a encontrarem o sitemap mesmo sem você o submeter
  manualmente no Search Console.
- Posição no repo: `/robots.txt` na raiz — GitHub Pages serve estático.

## Critério de aceite

1. `curl -s https://cookalaroulette.com/robots.txt` retorna exatamente o conteúdo acima.
2. `https://search.google.com/search-console` aceita sem erros (no relatório "robots.txt").
