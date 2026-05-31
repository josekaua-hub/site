/* ================================================================
   CALCULADORA FINANCEIRA — calculadora.js
   Lógica correta do ciclo agrícola:
     Receita = Quantidade Produzida × Preço Unitário  (entrada)
     Gastos  = soma dos custos variáveis + fixos       (saída)
     Saldo   = Receita − Gastos
   ================================================================ */

(function () {
  'use strict';

  /* ── Helpers ── */
  function val(id) {
    const el = document.getElementById(id);
    return el ? (parseFloat(el.value) || 0) : 0;
  }

  function set(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function fmt(n) {
    return 'R$ ' + n.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function fmtPct(n) {
    return n.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%';
  }

  /* ── Preview de receita em tempo real ── */
  function atualizarPreview() {
    const qtd   = val('qtdProduzida');
    const preco = val('precoUnitario');
    const total = qtd * preco;
    const preview = document.getElementById('fin-receita-preview');
    const est     = document.getElementById('fin-receita-est');
    if (preview && est) {
      if (qtd > 0 && preco > 0) {
        est.textContent = fmt(total);
        preview.style.display = 'flex';
      } else {
        preview.style.display = 'none';
      }
    }
  }

  /* ── Cálculo principal ── */
  function calcularFinanceiro() {
    const qtd   = val('qtdProduzida');
    const preco = val('precoUnitario');

    const sementes   = val('custoSementes');
    const adubo      = val('custoAdubo');
    const defensivos = val('custoDefensivos');
    const agua       = val('custoAgua');
    const maoObra    = val('custoMaoObra');
    const energia    = val('custoEnergia');
    const colheita   = val('custoColheita');
    const transporte = val('custoTransporte');
    const aluguel    = val('custoAluguel');
    const manutencao = val('custoManutencao');
    const ciclos     = Math.max(val('ciclosPorAno'), 1);

    /* Receita = entrada (colheita) */
    const receita = qtd * preco;

    /* Custos */
    const custosVar  = sementes + adubo + defensivos + agua + maoObra + energia + colheita + transporte;
    const custosFixC = (aluguel + manutencao) / ciclos;
    const custoTotal = custosVar + custosFixC;

    /* Saldo */
    const saldo = receita - custoTotal;

    /* Indicadores */
    const margemLucro = receita > 0 ? (saldo / receita) * 100 : 0;
    const roi         = custoTotal > 0 ? (saldo / custoTotal) * 100 : 0;
    const custoUnit   = qtd > 0 ? custoTotal / qtd : 0;
    const lucroUnit   = preco - custoUnit;
    /* Ponto de equilíbrio: só faz sentido quando preço > custo variável unitário */
    const custoVarUnit = qtd > 0 ? custosVar / qtd : 0;
    const peUnid = (preco > custoVarUnit && preco > 0)
      ? custosFixC / (preco - custoVarUnit)
      : 0;
    const peValor = peUnid * preco;

    /* Atualizar DOM */
    set('receitaTotal',          fmt(receita));
    set('custoTotal',            fmt(custoTotal));
    set('saldoFinal',            (saldo >= 0 ? '+ ' : '− ') + fmt(Math.abs(saldo)));
    set('margemLucro',           fmtPct(margemLucro));
    set('roi',                   fmtPct(roi));
    set('custoUnitario',         fmt(custoUnit));
    set('lucroUnitario',         fmt(lucroUnit));
    set('pontoEquilibrio',       peUnid.toLocaleString('pt-BR', {maximumFractionDigits:1}) + ' unid.');
    set('pontoEquilibrioValor',  fmt(peValor));
    set('custosVariaveis',       fmt(custosVar));
    set('custosFixosCiclo',      fmt(custosFixC));
    set('custoTotalCiclo',       fmt(custoTotal));

    /* Colorir saldo */
    const saldoEl = document.getElementById('saldoAlert');
    if (saldoEl) {
      saldoEl.classList.remove('lucro', 'prejuizo');
      saldoEl.classList.add(saldo >= 0 ? 'lucro' : 'prejuizo');
    }

    /* Atualizar saldo-val da barra de saldo se existir */
    const saldoValEl = document.getElementById('fin-saldo-ciclo-calc');
    if (saldoValEl) {
      saldoValEl.textContent = (saldo >= 0 ? '+ ' : '− ') + fmt(Math.abs(saldo));
      saldoValEl.className = 'fin-saldo-val fin-bold ' + (saldo >= 0 ? 'fin-verde' : 'fin-vermelho');
    }
  }

  /* ── Limpar ── */
  function limparFormulario() {
    const ids = [
      'qtdProduzida','precoUnitario',
      'custoSementes','custoAdubo','custoDefensivos','custoAgua',
      'custoMaoObra','custoEnergia','custoColheita','custoTransporte',
      'custoAluguel','custoManutencao',
    ];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = '0.00';
    });
    const ciclos = document.getElementById('ciclosPorAno');
    if (ciclos) ciclos.value = '1';

    const resetFmt = [
      'receitaTotal','custoTotal','saldoFinal','custoUnitario',
      'lucroUnitario','pontoEquilibrioValor','custosVariaveis',
      'custosFixosCiclo','custoTotalCiclo',
    ];
    resetFmt.forEach(id => set(id, 'R$ 0,00'));
    set('margemLucro', '0%');
    set('roi', '0%');
    set('pontoEquilibrio', '0 unid.');

    const saldoEl = document.getElementById('saldoAlert');
    if (saldoEl) saldoEl.classList.remove('lucro', 'prejuizo');

    const preview = document.getElementById('fin-receita-preview');
    if (preview) preview.style.display = 'none';
  }

  /* ── Simulador de cenários ── */
  function calcularCenario() {
    const preco   = val('precoUnitario');
    const qtd     = val('qtdProduzida');
    const vPreco  = val('variacaoPreco');
    const vQtd    = val('variacaoQtd');

    const novoPreco = preco * (1 + vPreco / 100);
    const novaQtd   = qtd   * (1 + vQtd   / 100);

    const sementes   = val('custoSementes');
    const adubo      = val('custoAdubo');
    const defensivos = val('custoDefensivos');
    const agua       = val('custoAgua');
    const maoObra    = val('custoMaoObra');
    const energia    = val('custoEnergia');
    const colheita   = val('custoColheita');
    const transporte = val('custoTransporte');
    const aluguel    = val('custoAluguel');
    const manutencao = val('custoManutencao');
    const ciclos     = Math.max(val('ciclosPorAno'), 1);

    const custoVar  = sementes + adubo + defensivos + agua + maoObra + energia + colheita + transporte;
    const custoFix  = (aluguel + manutencao) / ciclos;
    const custoTotal = custoVar + custoFix;

    const novaReceita = novaQtd * novoPreco;
    const novoSaldo   = novaReceita - custoTotal;

    set('novoPreco', fmt(novoPreco));
    set('novaQtd', novaQtd.toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + ' unid.');
    set('novoSaldo', (novoSaldo >= 0 ? '+ ' : '− ') + fmt(Math.abs(novoSaldo)));

    const novoSaldoEl = document.getElementById('novoSaldoAlert');
    if (novoSaldoEl) {
      novoSaldoEl.classList.remove('lucro', 'prejuizo');
      novoSaldoEl.classList.add(novoSaldo >= 0 ? 'lucro' : 'prejuizo');
    }

    const res = document.getElementById('resultadosCenario');
    if (res) res.style.display = 'flex';
  }

  /* ── Salvar fixos ── */
  function salvarFixos() {
    const a = document.getElementById('saveAluguel');
    const m = document.getElementById('saveManutencao');
    if (a) a.value = val('custoAluguel');
    if (m) m.value = val('custoManutencao');
    document.getElementById('saveFixosForm').submit();
  }

  /* ── Expor ao escopo global (chamados via onclick no HTML) ── */
  window.calcularFinanceiro = calcularFinanceiro;
  window.limparFormulario   = limparFormulario;
  window.calcularCenario    = calcularCenario;
  window.salvarFixos        = salvarFixos;

  /* ── Inicialização ── */
  document.addEventListener('DOMContentLoaded', function () {
    /* Preview ao digitar quantidade/preço */
    const qtdInp   = document.getElementById('qtdProduzida');
    const precoInp = document.getElementById('precoUnitario');
    if (qtdInp)   qtdInp.addEventListener('input', atualizarPreview);
    if (precoInp) precoInp.addEventListener('input', atualizarPreview);

    /* Recalcular automaticamente ao mudar qualquer custo */
    document.querySelectorAll('.custo-input').forEach(function (el) {
      el.addEventListener('change', calcularFinanceiro);
    });

    /* Se há prefill (campo selecionado), calcula automaticamente */
    if (qtdInp && parseFloat(qtdInp.value) > 0) {
      atualizarPreview();
      calcularFinanceiro();
    }
  });

})();
