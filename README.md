# Cook à la Roulette 🟠🎰

> O universo decide o que você vai cozinhar hoje.

**🌐 No ar em [cookalaroulette.com](https://cookalaroulette.com)** — clique e seja redirecionado para uma receita aleatória de chefs do mundo todo.

Um web app de página única que **sorteia uma receita aleatória** de um Chef curado e
**redireciona** para o site original. Sem login, sem fricção, sem conteúdo hospedado — a
aleatoriedade é o produto.

A tela é tipográfica e clicável: o nome **COOK À LA ROULETTE** em laranja sobre off-white,
com uma **fonte do Google Fonts sorteada a cada visita**. Clicou → uma breve animação →
abre uma receita real, de um Chef de algum canto do mundo.

## Como funciona

Dois componentes independentes que só conversam por um arquivo JSON (separação estrita):

```
  Frontend (HTML/CSS/JS puro)          Scraper (Python)
  index.html / style.css /        ←    scrapers/<site>.py  +  orquestrador.py
  app.js / sorteio.js                  coletam URLs de receita dos sites dos Chefs
        │  lê                                   │  gera/atualiza
        └────────────►  data/receitas.json  ◄───┘
                       [{chef, site, titulo, url}, ...]
```

- O **frontend** lê `data/receitas.json`, sorteia em duas etapas (Chef → receita) e
  redireciona. Não usa frameworks nem build. **Não usa IA em runtime.**
- O **scraper** roda offline/sob demanda (`python orquestrador.py`), coleta **apenas a
  localização** das receitas (nunca o conteúdo) e regrava o JSON. É Python determinístico —
  **também sem IA em runtime** (a IA ajudou só a *escrever* os adaptadores).

## Rodar

**Frontend** (precisa servir por HTTP — `fetch` não funciona via `file://`):

```bash
python3 -m http.server 8000      # na raiz do projeto
# abrir http://localhost:8000/
```

**Scraper** (opcional — só pra atualizar a curadoria):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium       # navegador p/ sites com JS/bloqueio
python orquestrador.py            # rodada completa: regrava data/receitas.json (foto nova)
python orquestrador.py --limite 25
python orquestrador.py --site jamieoliver --limite 2000   # cirúrgico: roda só 1 site e MESCLA
python orquestrador.py --site panelinha --site laylita    # vários específicos (preserva o resto)
```

> `--site MODULO` roda apenas o(s) adaptador(es) nomeado(s) (o nome do arquivo em `scrapers/`) e
> **mescla** no catálogo existente — substitui as receitas daquele site e preserva todos os outros
> chefs. Ideal para incluir/testar um site novo sem re-raspar os 30+. Sem `--site`, é tudo-ou-nada.

**Testes** (sem rede):

```bash
node tests/sorteio.test.js          # sorteio em duas etapas (distribuição ±10%)
python3 tests/test_orquestrador.py  # helpers do orquestrador
python3 tests/test_scrapers.py      # helpers de scraping
```

## Estrutura

```
index.html · style.css · app.js · sorteio.js   ← frontend (vanilla)
assets/favicon.svg                              ← "C" laranja (glifo Anton)
data/receitas.json                              ← curadoria (saída do scraper)
scrapers/  base.py + um arquivo por Chef        ← coleta (ver scrapers/README.md)
orquestrador.py · requirements.txt              ← orquestra a coleta
tests/                                          ← testes
specs/  001-… 002-… 003-…                       ← Spec Kit (spec/plan/tasks por fase)
.specify/memory/constitution.md                 ← princípios do projeto (v2.0.1)
BRIEFING.md                                      ← briefing original
```

## Técnicas de coleta (o scraper escolhe a mais simples que funcione)

1. **Sitemap** — lê o `sitemap.xml`/índice e filtra URLs de receita (técnica preferida).
2. **Sitemap via navegador** — Playwright pega o sitemap de sites que bloqueiam o cliente HTTP.
3. **Crawl BFS** — parte de uma página de listagem e segue "receitas relacionadas" (sites sem sitemap).
4. **Listagem** — extrai links de receita de páginas de índice.
5. **Wayback** — descobre URLs pelo Internet Archive quando o site está atrás de Cloudflare
   (sem contornar a proteção: o humano acessa normalmente; só descobrimos a localização).

## Fases (Spec Kit)

- **Fase 1 — Fundação** ✅ frontend + sorteio + dados manuais
- **Fase 2 — Scraper** ✅ infraestrutura + primeiros adaptadores
- **Fase 3 — Cobertura** ✅ ~30 Chefs de 25+ países (5 técnicas de coleta)
- **Fase 4 — Refinamento** ✅ acessibilidade WCAG AA, responsivo, roleta de fontes, OG/social, LICENSE, **deploy no ar**
- **Fase 5 — Expansão (Lista 2)** ✅ +52 chefs/marcas (food blogs, editoriais, coquetéis): **~93 mil receitas / 83 chefs**; modo cirúrgico `--site` no orquestrador
- **Fase 6 — Domínio + SEO** ✅ no ar em **https://cookalaroulette.com** (HTTPS via GitHub Pages); SEO em EN (`<title>`, `<meta description>`, `<link rel="canonical">`, JSON-LD Schema.org `WebSite`, OG/Twitter), `robots.txt` + `sitemap.xml`, **GoatCounter** como analytics privacy-friendly (sem cookies, evento custom `roleta-clique`), Search Console verificado

Princípios em [`.specify/memory/constitution.md`](.specify/memory/constitution.md).
Cada fase tem spec/plan/tasks em [`specs/`](specs/).
