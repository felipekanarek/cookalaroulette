/*
 * sorteio.js — lógica PURA do sorteio em duas etapas.
 *
 * Sem efeitos colaterais e sem dependência do DOM, para ser:
 *   - carregada no navegador via <script src="sorteio.js"> (funções no escopo global);
 *   - importada no Node pelo teste via require('../sorteio.js').
 *
 * Contrato de cada receita: { chef, site, titulo, url }  (ver contracts/receitas.schema.json)
 */

(function (global) {
  'use strict';

  // Valida um registro de receita conforme o contrato (FR-007).
  function receitaValida(r) {
    return (
      r &&
      typeof r.chef === 'string' && r.chef.trim() !== '' &&
      typeof r.site === 'string' && r.site.trim() !== '' &&
      typeof r.titulo === 'string' && r.titulo.trim() !== '' &&
      typeof r.url === 'string' && /^https?:\/\//.test(r.url.trim())
    );
  }

  // Agrupa receitas válidas por Chef. Retorna [{ chef, receitas: [...] }, ...]
  // contendo apenas Chefs com >= 1 receita válida (FR-007).
  function agruparPorChef(receitas) {
    if (!Array.isArray(receitas)) return [];
    const mapa = new Map();
    for (const r of receitas) {
      if (!receitaValida(r)) continue;
      const chave = r.chef.trim();
      if (!mapa.has(chave)) mapa.set(chave, []);
      mapa.get(chave).push(r);
    }
    return Array.from(mapa, ([chef, rs]) => ({ chef, receitas: rs }));
  }

  // Índice uniforme em [0, n). rng injetável para teste determinístico.
  function indiceUniforme(n, rng) {
    return Math.floor((rng || Math.random)() * n);
  }

  /*
   * Sorteio em duas etapas (FR-003, FR-004):
   *   1. sorteia um Chef uniformemente entre os Chefs elegíveis;
   *   2. sorteia uma receita uniformemente dentro desse Chef.
   * Retorna a receita sorteada, ou null se não houver Chef elegível.
   * `rng` opcional (função () => [0,1)) para testes.
   */
  function sortear(receitas, rng) {
    const chefs = agruparPorChef(receitas);
    if (chefs.length === 0) return null;
    const chef = chefs[indiceUniforme(chefs.length, rng)];
    return chef.receitas[indiceUniforme(chef.receitas.length, rng)];
  }

  const api = { receitaValida, agruparPorChef, sortear };

  // Exporta nos dois ambientes sem build.
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  } else {
    global.Sorteio = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
