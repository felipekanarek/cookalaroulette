/*
 * app.js — camada de UI do Cook à la Roulette.
 *
 * A tela inteira (um <button>) é o gatilho do sorteio. A cada visita, uma fonte é escolhida
 * aleatoriamente do Google Fonts. No clique: "roleta de fontes" (a tipografia troca de fonte
 * rápido por ~0,8s) e então redireciona para a receita original. Respeita prefers-reduced-motion.
 * A lógica de sorteio vive em sorteio.js (pura e testável).
 */

(function () {
  'use strict';

  const FONTE_DADOS = 'data/receitas.json';
  const DURACAO_GIRO = 800;   // ms (~0,8s) — FR-009
  const INTERVALO_GIRO = 80;  // ms entre trocas de fonte durante o giro

  const roleta = document.getElementById('roleta');
  const status = document.getElementById('status');

  let receitas = [];
  let girando = false;

  const MSG_VAZIO = 'Nenhuma receita disponível no momento.';
  const MSG_FALHA = 'Não foi possível carregar as receitas agora. Tente novamente mais tarde.';

  // Pool CURADO de fontes do Google Fonts (T002): display, legíveis em tamanho grande e que
  // cabem em telas estreitas. Removidas as problemáticas (pixel/sombra/mono muito largas:
  // Press Start 2P, Bungee Shade, Rubik Mono One, Monoton).
  const FONTES = [
    'Anton', 'Bebas Neue', 'Archivo Black', 'Oswald', 'Playfair Display', 'Abril Fatface',
    'Lobster', 'Pacifico', 'Staatliches', 'Righteous', 'Bowlby One', 'Titan One',
    'Passion One', 'Fjalla One', 'Alfa Slab One', 'Teko', 'Black Ops One', 'Bungee'
  ];
  // Subconjunto pré-carregado para o giro (evita flicker de fallback durante a roleta).
  const FONTES_GIRO = ['Anton', 'Bebas Neue', 'Archivo Black', 'Oswald', 'Abril Fatface',
                       'Staatliches', 'Righteous', 'Alfa Slab One'];

  function carregarFonte(nome) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=' + nome.replace(/ /g, '+') + '&display=swap';
    document.head.appendChild(link);
  }

  function aplicarFonte(nome) {
    document.documentElement.style.setProperty('--fonte', '"' + nome + '", Georgia, serif');
  }

  function aleatoria() {
    return FONTES[Math.floor(Math.random() * FONTES.length)];
  }

  const prefereMenosMovimento =
    window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Nova aba (preserva a roleta); fallback mesma aba. Não usar 'noopener' nas features
  // (faz window.open retornar null mesmo no sucesso → abriria nas duas abas).
  function redirecionar(url) {
    const nova = window.open(url, '_blank');
    if (nova) { nova.opener = null; } else { window.location.assign(url); }
  }

  function desabilitar(msg) { roleta.disabled = true; if (msg) status.textContent = msg; }
  function habilitar() { roleta.disabled = false; status.textContent = ''; }

  function finalizar(receita) {
    aplicarFonte(aleatoria());            // assenta numa fonte final
    roleta.removeAttribute('aria-busy');
    girando = false;
    roleta.disabled = false;
    redirecionar(receita.url);
  }

  // Clique: trava → roleta de fontes (~0,8s) → redireciona (FR-009/FR-013).
  function aoClicar() {
    if (girando || roleta.disabled) return;
    const receita = window.Sorteio.sortear(receitas);
    if (!receita) { desabilitar(MSG_VAZIO); return; }

    girando = true;
    roleta.disabled = true;
    roleta.setAttribute('aria-busy', 'true');

    if (prefereMenosMovimento) { finalizar(receita); return; }  // sem giro

    let n = 0;
    const giro = window.setInterval(function () {
      aplicarFonte(FONTES_GIRO[n % FONTES_GIRO.length]);
      n++;
    }, INTERVALO_GIRO);
    window.setTimeout(function () {
      window.clearInterval(giro);
      finalizar(receita);
    }, DURACAO_GIRO);
  }

  // Carrega a curadoria e define o estado (FR-002/FR-007/FR-008/FR-014 da Fase 1).
  function carregar() {
    desabilitar('Carregando…');
    fetch(FONTE_DADOS)
      .then(function (resp) {
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        return resp.json();
      })
      .then(function (dados) {
        if (!Array.isArray(dados)) throw new Error('formato inválido');
        if (window.Sorteio.agruparPorChef(dados).length === 0) { desabilitar(MSG_VAZIO); return; }
        receitas = dados;
        habilitar();
      })
      .catch(function () { desabilitar(MSG_FALHA); });  // FR-014: distinta da de lista vazia
  }

  // Fonte aleatória da visita (escolhe uma, carrega e aplica) + preload do conjunto de giro.
  var fonteDaVisita = aleatoria();
  carregarFonte(fonteDaVisita);
  aplicarFonte(fonteDaVisita);
  FONTES_GIRO.forEach(function (nome) {
    if (nome !== fonteDaVisita) carregarFonte(nome);
  });

  roleta.addEventListener('click', aoClicar);
  carregar();
})();
