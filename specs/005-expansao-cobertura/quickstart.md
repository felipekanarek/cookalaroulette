# Quickstart — Adicionar um site da Lista 2

Passo a passo para criar, validar e integrar um adaptador novo (vale para qualquer site da Lista 2).

## 1. Sondar a técnica

```bash
SITE=ciaosamin.com
curl -sI https://$SITE/sitemap.xml | head -3
curl -s  https://$SITE/robots.txt | grep -i sitemap
curl -sI https://$SITE/recipes/ | head -3
```

Decida: sitemap (preferido) → senão crawl/listagem → se JS, navegador → se Cloudflare total, wayback.

## 2. Escrever `scrapers/<site>.py`

Modelo mínimo (sitemap; adapte o filtro e a técnica):

```python
"""Adaptador: <Chef/Marca> (<País>) — via <técnica>."""
from __future__ import annotations
import re
from urllib.parse import urlparse
from . import base

CHEF = "Samin Nosrat"
SITE = "ciaosamin.com"
TECNICAS = ["sitemap"]
BASE_URL = "https://ciaosamin.com"

_NAO_RECEITA = {"about", "contact", "category", "tag", "recipes", "privacy-policy"}

def _e_receita(url: str) -> bool:
    p = urlparse(url)
    if p.netloc.replace("www.", "") != SITE:
        return False
    partes = [s for s in p.path.split("/") if s]
    if len(partes) != 1:                       # receita no slug-raiz: /slug/
        return False
    slug = partes[0].lower()
    if slug in _NAO_RECEITA or slug.isdigit():
        return False
    return bool(re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)+$", slug))

def coletar(limite: int) -> list[dict]:
    return base.coletar_por_sitemap(BASE_URL, CHEF, SITE, _e_receita, limite)
```

## 3. Validar isolado

```bash
python3 -c "from scrapers import ciaosamin; r=ciaosamin.coletar(10); print(len(r)); print(r[:3])"
```

Esperado: ≥1 (meta ≥10) registros com URLs de receita real. Ajuste `_e_receita` até limpar o ruído.

## 4. Registrar no orquestrador

Em `orquestrador.py`: adicione ao `from scrapers import (...)` e à lista `ADAPTADORES`.

## 5. Integrar ao catálogo (cirúrgico, preserva a Lista 1)

```bash
python3 orquestrador.py --site ciaosamin --limite 1000
# vários do lote de uma vez:
python3 orquestrador.py --site ciaosamin --site twospoons --site koreanbapsang --limite 1000
```

Confira o relatório (status `ok` + contagem) e o catálogo:

```bash
python3 -c "import json;d=json.load(open('data/receitas.json'));print(len(d),'receitas,',len({r['chef'] for r in d}),'chefs')"
```

## 6. Publicar

```bash
git add data/receitas.json scrapers/ orquestrador.py
git commit -m "feat: adiciona <Chef> (<site>)"
git push     # GitHub Pages republica
```

## Lote em paralelo (método das Fases 2/3)

Para um lote de ~8–10 sites, disparar sub-agentes (1 por site) que executam os passos 1–3 e
escrevem o adaptador; depois registrar todos (passo 4) e integrar o lote (passo 5) numa rodada
`--site`. Documentar integrados / sem-receitas / bloqueados / mortos com motivo (SC-005).
