/*
 * app.js — camada de UI do Cook a la Roulette.
 *
 * A tela inteira (um <button> em tela cheia) é o gatilho do sorteio. A cada visita,
 * uma fonte é escolhida aleatoriamente do Google Fonts. No clique: animação breve
 * (não-interativa) seguida do redirecionamento para a receita original.
 * A lógica de sorteio vive em sorteio.js (pura e testável).
 */

(function () {
  'use strict';

  const FONTE_DADOS = 'data/receitas.json';
  const DURACAO_ANIMACAO = 800; // ms (~0,8s) — FR-005

  const roleta = document.getElementById('roleta');
  const status = document.getElementById('status');

  let receitas = [];
  let girando = false;

  const MSG_VAZIO = 'Nenhuma receita disponível no momento.';
  const MSG_FALHA = 'Não foi possível carregar as receitas agora. Tente novamente mais tarde.';

  // --- Fonte aleatória do Google Fonts a cada visita ---------------------------------
  // Famílias variadas (display/serif/script) que ficam fortes em tamanho grande.
  const FONTES = [
    'Anton', 'Bebas Neue', 'Archivo Black', 'Oswald', 'Playfair Display', 'Abril Fatface',
    'Lobster', 'Pacifico', 'Monoton', 'Bungee', 'Staatliches', 'Righteous', 'Bowlby One',
    'Titan One', 'Rubik Mono One', 'Passion One', 'Fjalla One', 'Alfa Slab One', 'Teko',
    'Black Ops One', 'Bungee Shade', 'Press Start 2P'
  ];

  function aplicarFonteAleatoria() {
    const nome = FONTES[Math.floor(Math.random() * FONTES.length)];
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://fonts.googleapis.com/css2?family=' +
      nome.replace(/ /g, '+') + '&display=swap';
    document.head.appendChild(link);
    document.documentElement.style.setProperty('--fonte', '"' + nome + '", Georgia, serif');
    return nome;
  }

  const prefereMenosMovimento =
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Nova aba (preserva a roleta); fallback para a mesma aba se o popup for bloqueado.
  // Não usar 'noopener' nas features: faz window.open retornar null mesmo no sucesso,
  // o que abriria o link nas DUAS abas. Desanexamos o opener manualmente.
  function redirecionar(url) {
    const nova = window.open(url, '_blank');
    if (nova) {
      nova.opener = null;
    } else {
      window.location.assign(url);
    }
  }

  function desabilitar(msg) {
    roleta.disabled = true;
    if (msg) status.textContent = msg;
  }

  function habilitar() {
    roleta.disabled = false;
    status.textContent = '';
  }

  // Clique: trava → anima → sorteia → redireciona → destrava (FR-005 / FR-013).
  function aoClicar() {
    if (girando || roleta.disabled) return;
    const receita = window.Sorteio.sortear(receitas);
    if (!receita) { desabilitar(MSG_VAZIO); return; }

    girando = true;
    roleta.disabled = true;
    roleta.setAttribute('aria-busy', 'true');

    const espera = prefereMenosMovimento ? 0 : DURACAO_ANIMACAO;
    if (!prefereMenosMovimento) roleta.classList.add('saindo');

    window.setTimeout(function () {
      roleta.classList.remove('saindo');
      roleta.removeAttribute('aria-busy');
      girando = false;
      roleta.disabled = false;
      redirecionar(receita.url);
    }, espera);
  }

  // Carrega a curadoria e define o estado (FR-002 / FR-007 / FR-008 / FR-014).
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
      .catch(function () {
        desabilitar(MSG_FALHA); // FR-014: mensagem distinta da de lista vazia
      });
  }

  aplicarFonteAleatoria();
  roleta.addEventListener('click', aoClicar);
  carregar();
})();
