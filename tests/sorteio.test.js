/*
 * tests/sorteio.test.js — testes da lógica pura de sorteio.
 * Rodar:  node tests/sorteio.test.js
 * Sem framework: usa apenas o módulo `assert` nativo do Node.
 *
 * Cobre:
 *   - SC-003 / US2: distribuição uniforme por Chef (±10% em ≥1000 sorteios),
 *     independente do tamanho do catálogo de cada Chef.
 *   - FR-003/FR-004: a receita sorteada pertence ao Chef sorteado / existe na curadoria.
 *   - FR-007: registros inválidos e Chefs sem receita válida são excluídos.
 */

const assert = require('assert');
const { sortear, agruparPorChef, receitaValida } = require('../sorteio.js');

let passou = 0;
function teste(nome, fn) {
  fn();
  passou++;
  console.log('  ✓ ' + nome);
}

// Curadoria com catálogos de TAMANHOS DIFERENTES de propósito (1, 5 e 3 receitas).
function r(chef, n) {
  return { chef, site: 'exemplo.com', titulo: chef + ' #' + n, url: 'https://exemplo.com/' + chef + '/' + n };
}
const curadoria = [
  r('Ana', 1),
  r('Bia', 1), r('Bia', 2), r('Bia', 3), r('Bia', 4), r('Bia', 5),
  r('Caio', 1), r('Caio', 2), r('Caio', 3),
];

console.log('sorteio.js');

teste('agruparPorChef retorna apenas Chefs com receitas válidas', function () {
  const chefs = agruparPorChef(curadoria);
  assert.strictEqual(chefs.length, 3);
  const nomes = chefs.map(c => c.chef).sort();
  assert.deepStrictEqual(nomes, ['Ana', 'Bia', 'Caio']);
});

teste('FR-007: descarta registros inválidos e Chefs sem receita válida', function () {
  const sujo = [
    r('Ana', 1),
    { chef: 'SemUrl', site: 'x.com', titulo: 'x', url: '' },          // url vazia
    { chef: 'UrlRuim', site: 'x.com', titulo: 'x', url: 'ftp://x' },  // protocolo inválido
    { chef: '', site: 'x.com', titulo: 'x', url: 'https://x.com/a' }, // chef vazio
  ];
  assert.strictEqual(receitaValida(sujo[1]), false);
  assert.strictEqual(receitaValida(sujo[2]), false);
  const chefs = agruparPorChef(sujo);
  assert.strictEqual(chefs.length, 1);
  assert.strictEqual(chefs[0].chef, 'Ana');
});

teste('sortear retorna null para curadoria vazia ou inválida', function () {
  assert.strictEqual(sortear([]), null);
  assert.strictEqual(sortear(null), null);
  assert.strictEqual(sortear([{ chef: 'x', site: 's', titulo: 't', url: 'nope' }]), null);
});

teste('FR-003/FR-004: a receita sorteada sempre existe na curadoria', function () {
  for (let i = 0; i < 5000; i++) {
    const escolhida = sortear(curadoria);
    assert.ok(curadoria.includes(escolhida), 'receita fora da curadoria');
  }
});

teste('SC-003: cada Chef dentro de ±10% da frequência esperada (N=20000)', function () {
  const N = 20000;
  const contagem = { Ana: 0, Bia: 0, Caio: 0 };
  for (let i = 0; i < N; i++) {
    contagem[sortear(curadoria).chef]++;
  }
  const numChefs = 3;
  const esperado = N / numChefs;          // freq esperada se o sorteio do Chef é uniforme
  const tolerancia = 0.10 * esperado;     // ±10%
  for (const chef of Object.keys(contagem)) {
    const desvio = Math.abs(contagem[chef] - esperado);
    assert.ok(
      desvio <= tolerancia,
      `${chef}: ${contagem[chef]} (esperado ~${esperado.toFixed(0)}, desvio ${desvio.toFixed(0)} > tol ${tolerancia.toFixed(0)})`
    );
  }
  // Sanidade: Bia tem 5x mais receitas que Ana, mas NÃO é mais sorteada.
  console.log('    distribuição:', JSON.stringify(contagem));
});

console.log('\n' + passou + ' testes passaram.');
