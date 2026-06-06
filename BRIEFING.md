# Cook à la Roulette — Spec do Projeto

## Conceito

Um web app de página única que sorteia uma receita aleatória de um Chef curado, redirecionando o usuário para o site original do Chef. Sem login, sem fricção, sem conteúdo hospedado. A aleatoriedade é o produto.

O espírito: **o universo decide o que você vai cozinhar hoje**.

---

## Objetivos

### Produto

- Entregar uma experiência de descoberta culinária simples e sofisticada
- Expor o usuário a técnicas, sabores e culturas que ele não buscaria sozinho
- Conectar pessoas ao conteúdo original dos Chefs, sem intermediação

### Aprendizado técnico

- Aprender web scraping — como indexar receitas de sites externos de forma automatizada
- Entender a estrutura de projetos web do zero

---

## O que é / O que não é

| É | Não é |
|---|---|
| Um sorteador de receitas | Um repositório de receitas |
| Um redirecionador para conteúdo original | Um agregador de conteúdo |
| Uma experiência de descoberta | Um app de planejamento de refeições |
| Um projeto de aprendizado técnico | Um produto com login/perfil/histórico |

---

## Experiência do Usuário

### Fluxo principal

1. Usuário abre o site
2. Vê uma imagem limpa + um botão de ação central
3. Clica no botão
4. É redirecionado para uma receita aleatória no site original do Chef

### Princípios de design

- **Minimalista** — uma imagem, um botão, nada mais
- **Sofisticado** — não parece um sorteador de bingo
- **Responsivo** — funciona bem em mobile e desktop
- **Zero fricção** — sem cadastro, sem configuração, sem filtros

### O que NÃO aparece

- Filtros de culinária, tempo, dificuldade
- Lista de Chefs disponíveis
- Histórico de receitas sorteadas
- Login ou perfil

---

## Stack Tecnológica

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Scraper | Python + BeautifulSoup + Playwright | BeautifulSoup para sites estáticos, Playwright para sites dinâmicos (JS) |
| Dados | JSON | Simples, sem banco de dados, lido diretamente pelo frontend |
| Frontend | HTML + CSS + JavaScript puro | Sem frameworks, foco no aprendizado dos fundamentos |

### Separação de responsabilidades

- O **scraper** roda offline (ou agendado) e gera/atualiza o `receitas.json`
- O **frontend** lê o `receitas.json` e faz o sorteio no navegador
- Os dois projetos são independentes — você pode evoluir cada um sem mexer no outro

### Estratégia de scraping — adaptadores por Chef

Cada Chef tem um script próprio (`scrapers/nomesite.py`). Cada adaptador usa a técnica mais adequada para aquele site e produz sempre o mesmo formato de saída. O orquestrador chama todos e consolida o `receitas.json`.

```
scrapers/
  panelinha.py        ← BeautifulSoup (site estático)
  jamieoliver.py      ← BeautifulSoup (site estático)
  gordonramsay.py     ← Playwright (site dinâmico, talvez)
  ...
orquestrador.py       ← chama todos os adaptadores, gera receitas.json
```

### Técnicas de coleta (por ordem de preferência)

Para cada site, testar nessa ordem até encontrar o que funciona:

1. **Sitemap XML** — sites WordPress geram automaticamente um `sitemap.xml` com todas as URLs. É a forma mais completa e limpa. Verificar em `dominio.com/sitemap.xml`. Filtrar só URLs de receitas.
2. **BeautifulSoup** — quando o HTML já vem pronto do servidor. Bom para páginas de listagem com estrutura consistente (ex: `<h2>` com links de receita).
3. **Playwright** — quando o conteúdo é carregado por JavaScript (scroll infinito, botão "load more", SPAs). Abre um navegador real por baixo dos panos.

> **Aprendizado do RecipeTin Eats:** a página `/recipes/` só exibia 20 receitas recentes — o restante carrega via JS. O sitemap resolveu e entregou o catálogo completo.

**Regra:** todos os adaptadores retornam o mesmo formato:

```json
{
  "chef": "Jamie Oliver",
  "site": "jamieoliver.com",
  "titulo": "Spaghetti Carbonara",
  "url": "https://www.jamieoliver.com/recipes/pasta-recipes/spaghetti-carbonara/"
}
```

---

## Arquitetura Técnica

### Componentes

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)          │
│  Página única — imagem + botão          │
│  Lê receitas.json e sorteia             │
└────────────────────┬────────────────────┘
                     │ lê
┌────────────────────▼────────────────────┐
│           receitas.json                 │
│  Lista de URLs indexadas por Chef       │
│  Ex: { chef, site, url, titulo }        │
└────────────────────┬────────────────────┘
                     │ gera/atualiza
┌────────────────────▼────────────────────┐
│         Scraper (Python)                │
│  Visita os sites dos Chefs              │
│  Coleta URLs de receitas                │
│  Salva em receitas.json                 │
└─────────────────────────────────────────┘
```

### Sorteio em duas etapas

1. Sorteia um Chef da lista
2. Sorteia uma receita indexada desse Chef
3. Redireciona para a URL original

---

## Lista inicial de Chefs e Sites

| Chef | Site | País |
|------|------|------|
| Rita Lobo | panelinha.com.br | 🇧🇷 Brasil |
| Bela Gil | belagil.com | 🇧🇷 Brasil |
| Layla Pujol (Laylita) | laylita.com | 🇪🇨 Equador |
| Cecilia Tupac | ceciliatupac.com | 🇵🇪 Peru |
| Paulina Cocina | paulinacocina.net | 🇦🇷 Argentina |
| Pati Jinich | patijinich.com | 🇲🇽 México |
| Jamie Oliver | jamieoliver.com | 🇬🇧 Reino Unido |
| Nigella Lawson | nigella.com | 🇬🇧 Reino Unido |
| Gordon Ramsay | gordonramsay.com | 🇬🇧 Reino Unido |
| Yotam Ottolenghi | ottolenghi.co.uk | 🇬🇧 Reino Unido |
| Donal Skehan | donalskehan.com | 🇮🇪 Irlanda |
| Kenji López-Alt | seriouseats.com | 🇺🇸 EUA |
| Deb Perelman | smittenkitchen.com | 🇺🇸 EUA |
| Tieghan Gerard | halfbakedharvest.com | 🇺🇸 EUA |
| Joshua Weissman | joshuaweissman.com | 🇺🇸 EUA |
| Ina Garten | barefootcontessa.com | 🇺🇸 EUA |
| Akis Petretzikis | akispetretzikis.com | 🇬🇷 Grécia |
| David Lebovitz | davidlebovitz.com | 🇫🇷 França |
| Vincenzo's Plate | vincenzosplate.com | 🇮🇹 Itália |
| Flavia Imperatore (Misya) | misya.info | 🇮🇹 Itália |
| Omar Allibhoy | thespanishchef.com | 🇪🇸 Espanha |
| Joanna (Kwestia Smaku) | kwestiasmaku.com | 🇵🇱 Polônia |
| Dorota Świątkowska (Moje Wypieki) | mojewypieki.com | 🇵🇱 Polônia |
| Natasha Kravchuk | natashaskitchen.com | 🇺🇦 Ucrânia |
| Nevada Berg (North Wild Kitchen) | northwildkitchen.com | 🇳🇴 Noruega |
| Trine Hahnemann | trinehahnemann.com | 🇩🇰 Dinamarca |
| Linda Lomelino (Call Me Cupcake) | callmecupcake.se | 🇸🇪 Suécia |
| Ozoz Sokoh (Kitchen Butterfly) | kitchenbutterfly.com | 🇳🇬 Nigéria |
| Zoe Adjonyoh | zoesghana.com | 🇬🇭 Gana |
| Alida Ryder (Simply Delicious) | simply-delicious-food.com | 🇿🇦 África do Sul |
| Maangchi | maangchi.com | 🇰🇷 Coreia |
| Namiko Chen | justonecookbook.com | 🇯🇵 Japão |
| The Woks of Life | thewoksoflife.com | 🇨🇳 China |
| Sanjeev Kapoor | sanjeevkapoor.com | 🇮🇳 Índia |
| Pailin Chongchitnant | hot-thai-kitchen.com | 🇹🇭 Tailândia |
| Helen Le | danangcuisine.com | 🇻🇳 Vietnã |
| Nagi Maehashi | recipetineats.com | 🇦🇺 Austrália |
| Adam Liaw | adamliaw.com | 🇦🇺 Austrália |

> Lista inicial com 38 chefs de 25 países. Cresce com o tempo sem necessidade de mudança de arquitetura.

---

## Fora do Escopo (por ora)

- Filtros de qualquer tipo
- Login / perfil / histórico
- Hospedagem de conteúdo (fotos, texto, vídeo)
- App mobile nativo
- Notificações ou gamificação
- Parceria formal com os Chefs

---

## Fases do Projeto

### Fase 1 — Fundação

- Estrutura do projeto (pastas, ambiente, controle de versão)
- Frontend estático: página única com imagem e botão
- Lista de Chefs em arquivo de dados (JSON ou similar)
- Sorteio simples com URLs hardcoded para validar a experiência

### Fase 2 — Scraper

- Aprender e implementar scraping básico
- Indexar receitas dos primeiros 5 sites como experimento
- Entender as diferenças de estrutura HTML entre os sites
- Salvar URLs coletadas em arquivo/banco local

### Fase 3 — Integração

- Conectar scraper ao frontend
- Sorteio passa a usar URLs indexadas pelo scraper
- Cobrir todos os 25 sites iniciais

### Fase 4 — Refinamento

- Design final
- Responsividade
- Deploy público

---

## Perguntas em aberto

- Como lidar com sites que bloqueiam scraping?
- Com que frequência re-indexar as receitas?
