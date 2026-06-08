# Contrato — Interface de Adaptador de Site

Interface que TODO adaptador da Lista 2 (e da Lista 1) MUST cumprir. É o contrato interno entre
um adaptador e o `orquestrador.py` (Princípio V).

## Símbolos obrigatórios em `scrapers/<site>.py`

```python
CHEF: str        # nome do chef ou marca — ex.: "Samin Nosrat", "GialloZafferano"
SITE: str        # domínio — ex.: "ciaosamin.com"  (chave de mesclagem do modo --site)
TECNICAS: list   # ex.: ["sitemap"] | ["crawl"] | ["sitemap","playwright"] | ["wayback"]

def coletar(limite: int) -> list[dict]:
    """Retorna até `limite` registros {chef, site, titulo, url} de receitas reais e vivas."""
```

## Contrato de saída de `coletar(limite)`

- Retorna `list[dict]`, cada item: `{"chef": str, "site": str, "titulo": str, "url": str}`.
- Comprimento ≤ `limite`.
- Cada item passa em `base.registro_valido` (4 campos não vazios; url http(s)).
- Apenas URLs de **páginas de receita individual** (o filtro `_e_receita` exclui o resto).
- Coleta APENAS a localização (URL) — NUNCA o conteúdo da receita (Princípio III).
- Em bloqueio, MAY lançar `base.BloqueioError` (o orquestrador marca "bloqueado-pulado") ou
  retornar parcial; em falha inesperada, a exceção é isolada pelo orquestrador (não derruba os demais).

## Registro no orquestrador (obrigatório — FR-007)

```python
# orquestrador.py
from scrapers import (..., novosite)          # 1) import
ADAPTADORES = [..., novosite]                  # 2) inclusão na lista
```

## Técnicas disponíveis em `base.py` (reutilizar)

| Helper | Quando usar |
|--------|-------------|
| `coletar_por_sitemap(base_url, chef, site, _e_receita, limite, sub_filtro=None)` | Site com sitemap acessível (preferido). |
| `coletar_por_sitemap_browser(...)` | Sitemap servido só via navegador / bloqueia cliente HTTP. |
| `coletar_por_listagem(urls, chef, site, _e_receita, limite, usar_browser=False)` | Páginas de índice; `usar_browser=True` para listagem em JS. |
| `coletar_por_crawl(seeds, chef, site, _e_receita, limite, max_paginas=...)` | Sem sitemap; segue links de receita (BFS). |
| `coletar_por_wayback(dominio, chef, site, _e_receita, limite, cdx_filtro=None)` | Site totalmente atrás de Cloudflare. |

## Critério de aceite por adaptador

1. `python3 -c "from scrapers import <m>; print(len(<m>.coletar(10)))"` → ≥ 1 (meta da fase: ≥10).
2. As URLs retornadas abrem uma receita real (amostra conferida).
3. `_e_receita` não deixa passar não-receitas (categorias/autor/institucional).
4. Registrado no orquestrador; aparece no relatório com status `ok`.
