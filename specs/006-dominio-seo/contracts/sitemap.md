# Contrato — `sitemap.xml`

Arquivo XML na **raiz do site**: `https://cookalaroulette.com/sitemap.xml`.

## Conteúdo exato

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

## Regras

- Encoding: UTF-8.
- Apenas **1 URL** (a homepage canônica). Sem listagens de receitas — não somos agregadores
  (Princípio III).
- `<loc>` MUST ser exatamente o apex HTTPS com barra final: `https://cookalaroulette.com/`.
- `<lastmod>` no formato ISO 8601 (`YYYY-MM-DD`). Atualizar quando re-deployar significativamente.
- `<changefreq>` é dica, não regra — `monthly` reflete realisticamente quantas vezes a
  homepage muda materialmente.
- `<priority>` `1.0` — única página, prioridade máxima.

## Critério de aceite

1. `curl -s https://cookalaroulette.com/sitemap.xml` retorna o XML válido.
2. `xmllint --noout https://cookalaroulette.com/sitemap.xml` não acusa erro de parsing.
3. Search Console aceita a submissão sem erros.

## Evolução futura (fora do escopo)

Se um dia o produto ganhar páginas adicionais (improvável — fere Minimalismo Radical),
adicionar `<url>` blocos por página. Não há plano disto agora.
