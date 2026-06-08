# Feature Specification: Domínio próprio + SEO

**Feature Branch**: `006-dominio-seo`
**Created**: 2026-06-08
**Status**: Draft
**Input**: User description: "Fase 6 — publicar o Cook à la Roulette em `cookalaroulette.com` (GitHub Pages + HTTPS) e prepará-lo para ser encontrado no Google, sem ferir o Minimalismo Radical da tela."

## Clarifications

### Session 2026-06-08

- Q: Idioma principal das metas SEO (`<title>`, `<meta description>`, JSON-LD)? → A: **EN principal**. O catálogo é majoritariamente em inglês e o alcance internacional é maior. O atributo `lang="pt-BR"` da página permanece (afeta acessibilidade/leitura, não SEO). Sem `hreflang` por ora.
- Q: Cadastro no Google Search Console entra no escopo? → A: **Sim**. Verificação via meta tag `google-site-verification` no `<head>` + submissão do `sitemap.xml`.
- Q: Algum analytics nesta fase? → A: **Sim — GoatCounter** (privacy-friendly, sem cookies, sem banner de consentimento, grátis para uso pessoal). Conta visitas, referrer e **um evento custom de "clique na roleta"** (para medir taxa visita→clique). Implementação: 1 linha de `<script>` no `<head>` + 1 linha em `app.js` no `aoClicar()` para disparar o evento. Não fere Zero Fricção nem Minimalismo Radical (sem elemento visível novo na tela). Constitui exceção mínima ao Princípio VI no mesmo espírito do Google Fonts via CDN — documentar.
- Q: O que fazer com o subdomínio `.github.io` antigo? → A: **Manter com redirect 301 automático** para `cookalaroulette.com` (comportamento padrão do GitHub após Custom Domain). Canonical concentra autoridade SEO no domínio novo sem quebrar links antigos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Site no domínio próprio com HTTPS (Priority: P1)

Como visitante do Cook à la Roulette, ao digitar `cookalaroulette.com` (ou `https://cookalaroulette.com`)
quero abrir o app exatamente como já abre hoje em `felipekanarek.github.io/cookalaroulette/` —
mesma tela, mesmo comportamento, com cadeado HTTPS válido no navegador.

**Why this priority**: É o trabalho-base que permite tudo o mais (SEO, compartilhamento social,
identidade da marca). Sem domínio próprio, a presença pública continua "técnica" demais.

**Independent Test**: abrir `https://cookalaroulette.com` em um navegador limpo (sem cache, sem
cookies) e verificar: (a) carrega a mesma tela do `.github.io`; (b) cadeado HTTPS válido;
(c) clique sorteia e redireciona; (d) `https://www.cookalaroulette.com` resolve para o mesmo
destino (ou redireciona ao apex); (e) o `.github.io/cookalaroulette/` antigo redireciona
automaticamente para o domínio novo.

**Acceptance Scenarios**:

1. **Given** o DNS está propagado e o GitHub Pages emitiu o certificado, **When** acesso
   `https://cookalaroulette.com`, **Then** vejo a tela "COOK À LA ROULETTE" idêntica à atual,
   com HTTPS válido, e o clique sorteia e redireciona como antes.
2. **Given** o domínio está no ar, **When** acesso `http://cookalaroulette.com`, **Then** sou
   redirecionado para `https://` (Enforce HTTPS).
3. **Given** o domínio está no ar, **When** acesso o subdomínio antigo
   `felipekanarek.github.io/cookalaroulette/`, **Then** sou redirecionado para o domínio novo
   (comportamento padrão do GitHub Pages após `Custom domain`).

---

### User Story 2 - Encontrável no Google pela marca e por intenção (Priority: P1)

Como pessoa que conheceu o produto de ouvido ou que tem curiosidade sobre "sorteador de receitas",
quero **achar o Cook à la Roulette no Google** ao digitar o nome da marca ou frases de intenção
como "o que cozinhar hoje" / "sorteador de receitas aleatórias" / "random recipe roulette" —
sem precisar do link direto.

**Why this priority**: A presença pública só vira "produto descobrível" depois que o Google
indexa, entende e mostra. Esta é a meta de existência social do site.

**Independent Test**: depois de uma janela razoável (≤ 30 dias da troca de domínio + submissão
do sitemap), buscar no Google "cook à la roulette" e ver o site na 1ª página com título e
descrição corretos; buscar uma query de intenção e ver pelo menos uma impressão no Search
Console; verificar que o snippet de compartilhamento (OG/Twitter) usa o domínio novo.

**Acceptance Scenarios**:

1. **Given** o domínio próprio está no ar e o sitemap foi submetido ao Google, **When** o
   robô do Google rastreia o site, **Then** a homepage canônica é `https://cookalaroulette.com/`
   (única — não há duplicata indexada via `.github.io`).
2. **Given** o site está indexado, **When** alguém busca pelo nome da marca, **Then** o site
   aparece na 1ª página com o `<title>` e a `<meta description>` corretos.
3. **Given** alguém compartilha o link em rede social, **When** a prévia carrega, **Then** a
   imagem OG (1200×630) e o título usam o domínio novo (não o `.github.io`).

---

### User Story 3 - Tela continua minimalista (Priority: P1 — invariante constitucional)

Como mantenedor do Cook à la Roulette, exijo que TODA mudança desta fase aconteça em
`<head>`, em arquivos auxiliares (`robots.txt`, `sitemap.xml`, `CNAME`) e em metadados do repo
— NUNCA na tela. A página continua exibindo apenas o texto-marca `COOK À LA ROULETTE`.

**Why this priority**: É um invariante constitucional (Princípio I — Minimalismo Radical). Não é
"prioridade" no sentido convencional; é uma trava de aceitação que vale para a fase inteira.

**Independent Test**: comparar visualmente a página antes e depois da fase (mesma fonte
sorteada, mesmo viewport) — devem ser pixel-equivalentes (a roleta de fontes é variabilidade
intencional, não conta). Inspecionar o DOM `<body>` — nenhum elemento novo permanente foi
adicionado.

**Acceptance Scenarios**:

1. **Given** a fase está implementada, **When** abro a página, **Then** vejo exatamente o mesmo
   layout, cores e tipografia (modulo a roleta aleatória da Fase 4).
2. **Given** a fase está implementada, **When** inspeciono o `<body>` no DevTools, **Then** não
   há nenhum elemento visível novo (sem banner de cookies, sem widget de analytics, sem badge).

---

### Edge Cases

- **Janela de propagação DNS** (até 24h): durante a propagação, o domínio pode resolver
  parcialmente; o subdomínio `.github.io` deve continuar servindo o site sem interrupção.
- **Certificado HTTPS ainda não emitido**: o GitHub Pages pode levar minutos a horas para
  emitir o certificado após a configuração do `Custom domain`. Não habilitar "Enforce HTTPS"
  antes do certificado estar disponível.
- **Apex vs www**: ambos devem resolver; uma das formas é canônica e a outra redireciona.
- **`.github.io` indexado em paralelo**: sem canonical, o Google poderia tratar como duplicata.
  O `<link rel="canonical">` para o domínio novo previne isso; o redirect automático do GitHub
  após `Custom domain` reforça.
- **Search Console com domínio recém-criado**: pode demorar dias até aparecer impressões. Isso
  é inerente ao Google e não é falha desta fase.
- **Erros de DNS** (registros A errados, ausência do CNAME no www): o GitHub mostra warnings na
  página de Settings → Pages; corrigir antes de habilitar HTTPS.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST ser acessível em `https://cookalaroulette.com` com certificado
  HTTPS válido emitido pelo GitHub Pages.
- **FR-002**: O acesso a `http://cookalaroulette.com` MUST redirecionar para a versão HTTPS
  (Enforce HTTPS habilitado).
- **FR-003**: O acesso ao subdomínio antigo (`https://felipekanarek.github.io/cookalaroulette/`)
  MUST redirecionar automaticamente para `https://cookalaroulette.com/` (comportamento padrão
  do GitHub Pages após configuração do `Custom domain`).
- **FR-004**: O repositório MUST conter um arquivo `CNAME` na raiz com o conteúdo
  `cookalaroulette.com` (criado pelo GitHub ao configurar Custom domain; preservado nos commits).
- **FR-005**: A homepage MUST declarar uma URL canônica via `<link rel="canonical">` apontando
  para `https://cookalaroulette.com/`.
- **FR-006**: A homepage MUST conter um `<title>` e uma `<meta name="description">` em **inglês**
  (idioma principal de SEO), orientados para as queries-alvo: nome da marca ("Cook à la Roulette"),
  intenção ("random recipe roulette", "what should I cook", "recipe randomizer"), e termos
  secundários em pt-BR ("sorteador de receitas", "o que cozinhar hoje") quando couber sem
  prejudicar a clareza em inglês. O atributo `lang="pt-BR"` da página permanece.
- **FR-007**: A homepage MUST conter um bloco `<script type="application/ld+json">` com
  Schema.org tipo `WebSite`, declarando nome, descrição, URL e idioma do produto.
- **FR-008**: As metas Open Graph e Twitter Cards (já existentes na Fase 4) MUST ser atualizadas
  para usar `https://cookalaroulette.com/` em `og:url`, `og:image` e `twitter:image`.
- **FR-009**: A raiz do site MUST servir um `robots.txt` que (a) permite rastreamento geral por
  bots legítimos e (b) declara a localização do `sitemap.xml`.
- **FR-010**: A raiz do site MUST servir um `sitemap.xml` listando ao menos a homepage canônica
  com sua data de última modificação.
- **FR-011**: A propriedade do domínio MUST ser verificável pelo Google Search Console — seja
  via DNS TXT record, seja via meta tag de verificação no `<head>` (`google-site-verification`).
  (O cadastro efetivo no Search Console é uma ação operacional do mantenedor — ver Assumptions.)
- **FR-012**: As referências a URL absoluta fora do `<head>` (README.md, `gh repo edit
  --homepage`, memória do projeto) MUST ser atualizadas para o domínio novo.
- **FR-013**: NENHUM elemento visível permanente MUST ser adicionado ao `<body>` por esta fase
  (Princípio I — Minimalismo Radical).
- **FR-014**: Esta fase MUST NÃO tocar o scraper, o sorteio, o frontend visual ou o contrato de
  dados `{chef, site, titulo, url}` (Princípio IV — Separação Estrita). A única exceção é uma
  chamada `goatcounter.count({event: true, path: 'roleta-clique'})` adicionada ao handler do
  clique em `app.js` — não altera o comportamento do sorteio, só registra o evento.
- **FR-015**: A homepage MUST incluir o script do GoatCounter no `<head>` (~3 KB, async, sem
  cookies, sem banner de consentimento). O script MUST falhar silenciosamente se o GoatCounter
  estiver fora do ar — o sorteio e o redirecionamento NÃO podem depender dele.
- **FR-016**: O clique de sorteio (`aoClicar`) MUST disparar um evento `roleta-clique` no
  GoatCounter (best-effort: chamar apenas se `window.goatcounter` existir).

### Key Entities *(include if feature involves data)*

- **Domínio canônico** (`cookalaroulette.com`): identidade pública do produto; substitui o
  subdomínio do GitHub como endereço primário.
- **Metas SEO no `<head>`**: conjunto declarativo de hints para crawlers — `<title>`,
  `<meta description>`, canonical, Open Graph, Twitter Card, Schema.org JSON-LD,
  `google-site-verification` (se via meta).
- **Arquivos auxiliares na raiz do repo**: `CNAME`, `robots.txt`, `sitemap.xml`.
- **Indexação no Google**: estado externo (não-armazenado pelo projeto), observável via
  Search Console e via buscas reais.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `https://cookalaroulette.com` carrega a aplicação corretamente em ≤ 2 segundos
  na primeira visita (rede 4G típica), com cadeado HTTPS válido.
- **SC-002**: Acessar `http://cookalaroulette.com`, `https://www.cookalaroulette.com` e
  `https://felipekanarek.github.io/cookalaroulette/` leva, em todos os três casos, ao mesmo
  destino final `https://cookalaroulette.com/` (apex HTTPS), com no máximo 1 redirect.
- **SC-003**: Em até 30 dias após a troca de domínio + submissão do sitemap, buscar
  "cook à la roulette" no Google em uma janela anônima mostra o site **na 1ª página de
  resultados**, com o `<title>` e a `<meta description>` configurados.
- **SC-004**: Em até 30 dias, o Google Search Console registra pelo menos **1 impressão para a
  query do nome da marca** e indica a homepage canônica como `https://cookalaroulette.com/`.
- **SC-005**: O Lighthouse SEO score da homepage no domínio novo é ≥ **90/100** (auditoria com
  Chrome em modo móvel).
- **SC-006**: Comparação visual da homepage (mesmo viewport, mesma fonte se fixarmos
  `--fonte` para o teste) entre antes e depois da fase é **pixel-equivalente no `<body>`** —
  nenhum elemento visível permanente foi adicionado (validação manual + inspeção do DOM).
- **SC-007**: A versão `.github.io` antiga **não aparece** mais nos resultados do Google para
  buscas do nome da marca dentro de 60 dias (indicando que o canonical + redirect
  consolidaram a autoridade no domínio novo).
- **SC-008**: O painel do GoatCounter mostra contagem de **visitas** e de **eventos
  `roleta-clique`** dentro de 24h após o deploy da Fase 6. Em qualquer momento posterior, o
  mantenedor consegue responder "quantos acessos e quantos cliques tivemos hoje/semana/mês?"
  abrindo o painel.

## Assumptions

Decisões-padrão tomadas na ausência de definição explícita (a confirmar em `/speckit-clarify`):

- **Domínio**: `cookalaroulette.com` (escolhido pelo mantenedor; compra/renovação fora do escopo
  do código — é responsabilidade operacional).
- **Apex × www**: o apex `cookalaroulette.com` é a forma canônica; `www.cookalaroulette.com`
  redireciona para o apex (configurado no provedor de DNS conforme suporte; tipicamente CNAME
  do www → `felipekanarek.github.io` + GitHub Pages decide o redirect).
- **Idioma principal de SEO** (clarificado): **EN** — `<title>`, `<meta description>` e JSON-LD
  em inglês para mirar alcance internacional, com termos pt-BR secundários quando couberem. O
  atributo `lang="pt-BR"` da página permanece (não muda — afeta acessibilidade/leitura, não a
  intenção de SEO). Sem `hreflang` separado por ora.
- **Search Console**: dentro do escopo desta fase. Verificação via meta tag
  `google-site-verification` no `<head>` (mais simples, não depende de acesso ao DNS depois) e
  submissão do `sitemap.xml`.
- **Analytics** (clarificado): **GoatCounter** — privacy-friendly (sem cookies, sem coleta de
  dados pessoais, sem banner LGPD/GDPR exigido), 1 linha de `<script>` no `<head>` + 1 chamada
  no `aoClicar` para o evento custom `roleta-clique`. Mede visitas, referrer, países, e a
  taxa visita→clique. Conta gratuita (uso pessoal). O carregamento é assíncrono e falha
  silenciosamente — o produto continua funcionando se o serviço cair.
- **Constitucional**: o script externo do GoatCounter é uma **exceção documentada ao Princípio
  VI**, no mesmo espírito da exceção já aberta para Google Fonts via CDN. Sem cookies e sem
  elemento visível, não conflita com Zero Fricção nem Minimalismo Radical.
- **`.github.io` antigo**: mantido acessível, redirecionando automaticamente para o domínio
  novo (comportamento padrão do GitHub após `Custom domain` — não vamos bloqueá-lo via robots).
  O canonical concentra autoridade SEO no domínio novo sem precisar quebrar o link antigo.
- **Bing Webmaster Tools** e outros buscadores não-Google: fora do escopo desta fase (podem
  vir depois sem custo).
- **Conteúdo do sitemap**: apenas a homepage. Não vamos listar receitas em massa (Princípio
  III — não hospedamos conteúdo); cada receita já está no sitemap do site original do chef.
- **Período de medição dos SC-003/004/007**: dias-corridos a partir do dia em que o domínio
  resolve em HTTPS e o sitemap foi submetido — não da abertura da spec.
- **Dependências**: GitHub Pages (já em uso), DNS do registrador escolhido pelo usuário, Google
  Search Console (conta gratuita do mantenedor).
- **Fora de escopo desta fase**: link building, anúncios pagos, redes sociais, mudanças
  visuais, analytics, blog/conteúdo próprio, automação de CI, alterações no scraper ou no
  contrato de dados.
