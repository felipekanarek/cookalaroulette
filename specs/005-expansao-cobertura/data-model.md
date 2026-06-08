# Data Model — Expansão de Cobertura (Lista 2)

O modelo é o **já existente** (Fases 2–4); esta fase não introduz entidades nem campos novos.
Documentado aqui para referência e validação.

## Entidades

### Registro de Receita (unidade do catálogo) — INALTERADO

| Campo | Tipo | Regra |
|-------|------|-------|
| `chef` | string | Nome do chef OU da marca/editorial (ex.: "Samin Nosrat", "GialloZafferano"). Não vazio. |
| `site` | string | Domínio de origem (ex.: "saveur.com"). Usado como chave de mesclagem no modo `--site`. Não vazio. |
| `titulo` | string | Título legível da receita (derivado do slug/URL). Não vazio. |
| `url` | string (URL) | URL absoluta da receita original. Única (após normalização). Deve estar viva (2xx ou 401/403/429). |

Validação: `base.registro_valido(r)` — exige os 4 campos não vazios e `url` http(s).
Unicidade: `normalizar_url` (host minúsculo, sem barra final, sem fragmento) → dedup global.

### Adaptador de Site — um por site (Princípios V e VIII)

Módulo `scrapers/<site>.py` expondo:

| Símbolo | Tipo | Descrição |
|---------|------|-----------|
| `CHEF` | str | Nome do chef/marca (vai para o campo `chef`). |
| `SITE` | str | Domínio (vai para o campo `site`; chave de mesclagem). |
| `TECNICAS` | list[str] | Técnicas usadas (só para o relatório; ex.: `["sitemap"]`). |
| `coletar(limite: int)` | função | Retorna `list[dict]` de registros no contrato, no máximo `limite`. |
| `_e_receita(url)` (interno) | função | Predicado que decide se uma URL é receita individual. |

### Catálogo (`data/receitas.json`) — INALTERADO

Lista de Registros de Receita. Cresce por **mesclagem cirúrgica**: o modo `--site` substitui os
registros cujos `site` foram rodados e preserva todos os demais (Lista 1). Gravação atômica.

### Relatório de Coleta (efêmero, por rodada)

Por adaptador: `{site, chef, tecnica, coletadas, status}` onde `status` ∈
{`ok`, `sem-receitas`, `bloqueado-pulado (...)`, `erro (...)`}. Base da prestação de contas (US3/SC-005).

## Relacionamentos

```
Adaptador (1) ──produz──> (N) Registro de Receita ──compõe──> Catálogo
       │                                                          ▲
       └── registrado em orquestrador.py (ADAPTADORES) ──gera/mescla──┘
Frontend ──lê──> Catálogo   (somente leitura; intocado nesta fase)
```

## Invariantes

- INV-1: todo registro no catálogo satisfaz `registro_valido`.
- INV-2: 0 duplicatas por `normalizar_url` no catálogo final (SC-004).
- INV-3: os `site` da Lista 1 permanecem presentes após a integração (SC-003).
- INV-4: nenhuma alteração no conjunto de campos do contrato (Princípio V).
