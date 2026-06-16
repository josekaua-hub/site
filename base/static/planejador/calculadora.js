/* ================================================================
   PLANEJADOR DE PLANTIO — calculadora.js  (v2 2026-05-31)
   Melhorias:
   - Preview em tempo real de covas/varas ao digitar área/espaçamento
   - Indicadores de faixa de solo (baixo/médio/alto) por nutriente
   - Resultados em cards visuais por insumo
   - Custo inline por insumo, total no final
   - Seções colapsáveis do formulário
   - Uso de MO para ajuste de nitrogênio (> 3.5% → reduz 10 kg/ha)
================================================================ */

'use strict';

/* ── Helpers ────────────────────────────────────────────────────── */
const moeda = new Intl.NumberFormat('pt-BR', { style:'currency', currency:'BRL' });

function lerNum(id, def = null) {
  const el = document.getElementById(id);
  if (!el) return def;
  const v = el.value.trim().replace(',', '.');
  if (v === '') return def;
  const n = parseFloat(v);
  return isNaN(n) ? def : n;
}

function fmt(n, dec = 1) {
  if (n === null || n === undefined || !isFinite(n)) return '—';
  return n.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: dec });
}

function ajustarSacosMinimos(sacos) {
  return sacos > 0 && sacos < 1 ? 1 : sacos;
}

/* ── Faixas de classificação de solo ────────────────────────────── */
function faixaFosforo(p) {
  if (p === null) return null;
  if (p <= 10)  return { label:'Muito baixo', cls:'plj-faixa-baixo',  dose:60 };
  if (p <= 20)  return { label:'Baixo',        cls:'plj-faixa-baixo',  dose:40 };
  return              { label:'Médio/Alto',    cls:'plj-faixa-alto',   dose:20 };
}

function faixaPotassio(k) {
  if (k === null) return null;
  if (k <= 0.05)  return { label:'Muito baixo', cls:'plj-faixa-baixo',  dose:40 };
  if (k <= 0.10)  return { label:'Baixo',        cls:'plj-faixa-baixo',  dose:30 };
  if (k <= 0.15)  return { label:'Médio',        cls:'plj-faixa-medio',  dose:20 };
  return               { label:'Alto',           cls:'plj-faixa-alto',   dose:0  };
}

function faixaSaturacao(v) {
  if (v === null) return null;
  if (v < 40)  return { label:'Baixa — precisa de calcário', cls:'plj-faixa-baixo'  };
  if (v < 60)  return { label:'Média — verificar calcário',  cls:'plj-faixa-medio'  };
  return             { label:'Adequada — sem calcário',      cls:'plj-faixa-alto'   };
}

function renderFaixa(idSpan, info) {
  const el = document.getElementById(idSpan);
  if (!el) return;
  if (!info) { el.innerHTML = ''; return; }
  el.innerHTML = `<span class="plj-faixa ${info.cls}">${info.label}</span>`;
}

/* ── Preview de plantio em tempo real ──────────────────────────── */
function atualizarPreviewPlantio() {
  const A = lerNum('id_area');
  const L = lerNum('id_linhas', 1.0);
  const P = lerNum('id_plantas', 0.8);
  const el = document.getElementById('preview-plantio');
  const badge = document.getElementById('badge-area');

  if (!el) return;

  if (A && A > 0 && L > 0 && P > 0) {
    const ha    = A / 10000;
    const covas = Math.ceil((A / (L * P)) * 1.1);
    const varas = Math.ceil(covas / 5);
    el.style.display = 'block';
    el.innerHTML = `
      🌱 <strong>${fmt(covas, 0)} covas</strong> &nbsp;·&nbsp;
      🪵 <strong>${fmt(varas, 0)} varas</strong>
      <span style="opacity:0.6; margin-left:6px;">(${fmt(ha, 4)} ha)</span>`;
    if (badge) badge.innerHTML = `<span class="plj-live-badge">${fmt(ha,4)} ha</span>`;
  } else {
    el.style.display = 'none';
    if (badge) badge.innerHTML = '';
  }
}

/* ── Indicadores de faixa ao digitar ────────────────────────────── */
function atualizarFaixas() {
  renderFaixa('faixa-fosforo',   faixaFosforo(lerNum('id_fosforo')));
  renderFaixa('faixa-potassio',  faixaPotassio(lerNum('id_potassio')));
  renderFaixa('faixa-saturacao', faixaSaturacao(lerNum('id_saturacao')));
}

/* ── Seções colapsáveis ─────────────────────────────────────────── */
function toggleSecao(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('aberta');
}
window.toggleSecao = toggleSecao;

/* ══════════════════════════════════════════════════════════════════
   CALCULAR PRINCIPAL
══════════════════════════════════════════════════════════════════ */
function calcular() {
  const A      = lerNum('id_area');
  const L      = lerNum('id_linhas', 1.0);
  const P      = lerNum('id_plantas', 0.8);
  const Psolo  = lerNum('id_fosforo');
  const Ksolo  = lerNum('id_potassio');
  const V1     = lerNum('id_saturacao');
  const T      = lerNum('id_ctc');
  const PRNT   = lerNum('id_calcario', 80);
  const MO     = lerNum('id_materia');
  const doseNInput = lerNum('id_nitrogenio');

  const pPrecoP  = lerNum('id_preco_fosforo');
  const pPrecoK  = lerNum('id_preco_potassio');
  const pPrecoN  = lerNum('id_preco_nitrogenio');
  const pPrecoC  = lerNum('id_preco_calcario');
  const temPreco = (pPrecoP !== null || pPrecoK !== null || pPrecoN !== null || pPrecoC !== null);

  const resultado = document.getElementById('resultado');

  /* Validação */
  if (!A || A <= 0) {
    resultado.style.display = 'block';
    resultado.innerHTML = `<div class="plj-erro">⚠️ Informe a <strong>Área total</strong> (campo obrigatório).</div>`;
    return;
  }
  if (doseNInput !== null && doseNInput < 0) {
    resultado.style.display = 'block';
    resultado.innerHTML = `<div class="plj-erro">⚠️ A dose de Nitrogênio deve ser ≥ 0.</div>`;
    return;
  }

  const areaHa = A / 10000;
  let html = '';
  let custoTotal = 0;
  let temCusto   = false;

  /* ── 1. Plantio ─────────────────────────────────────────────── */
  const covas = Math.ceil((A / (L * P)) * 1.1);
  const varas  = Math.ceil(covas / 5);
  html += `
    <div class="plj-resultado-titulo">🌱 Plantio e Mudas</div>
    <div class="plj-cards">
      <div class="plj-card">
        <span class="plj-card-icone">⛏️</span>
        <div class="plj-card-info">
          <div class="plj-card-nome">Total de Covas</div>
          <div class="plj-card-detalhe">Com 10% de margem de segurança (espaçamento ${fmt(L,2)} m × ${fmt(P,2)} m)</div>
        </div>
        <div class="plj-card-qty">
          <span class="plj-card-qty-val">${fmt(covas,0)}</span>
          <span class="plj-card-qty-unit">manivas</span>
        </div>
      </div>
      <div class="plj-card">
        <span class="plj-card-icone">🪵</span>
        <div class="plj-card-info">
          <div class="plj-card-nome">Total de Varas</div>
          <div class="plj-card-detalhe">1 vara de 1 m rende 5 manivas de 20 cm</div>
        </div>
        <div class="plj-card-qty">
          <span class="plj-card-qty-val">${fmt(varas,0)}</span>
          <span class="plj-card-qty-unit">varas</span>
        </div>
      </div>
    </div>`;

  /* ── 2. Insumos ─────────────────────────────────────────────── */
  const insumoCards = [];

  // Fósforo
  if (Psolo !== null && Psolo >= 0) {
    const fP   = faixaFosforo(Psolo);
    const dp   = fP.dose;
    const kgP  = dp * areaHa;
    const sacP = Math.ceil(ajustarSacosMinimos(kgP / 50));
    let custoStr = '';
    if (temPreco && pPrecoP !== null && sacP > 0) {
      const custo = sacP * pPrecoP;
      custoTotal += custo;
      temCusto = true;
      custoStr = `<div class="plj-card-custo">💰 ${fmt(sacP,0)} sacos × ${moeda.format(pPrecoP)} = <strong>${moeda.format(custo)}</strong></div>`;
    }
    insumoCards.push(kgP === 0
      ? `<div class="plj-card sem-correcao">
          <span class="plj-card-icone">💜</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Fósforo (P₂O₅)</div>
            <div class="plj-card-detalhe">Solo ${fP.label} — sem necessidade de correção</div>
          </div>
          <div class="plj-card-qty"><span class="plj-card-qty-val">—</span></div>
         </div>`
      : `<div class="plj-card">
          <span class="plj-card-icone">💜</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Fósforo (P₂O₅)</div>
            <div class="plj-card-detalhe">Solo ${fP.label} → dose ${dp} kg/ha · ${fmt(kgP,1)} kg total${custoStr}</div>
          </div>
          <div class="plj-card-qty">
            <span class="plj-card-qty-val">${sacP}</span>
            <span class="plj-card-qty-unit">sacos 50 kg</span>
          </div>
         </div>`);
  }

  // Potássio
  if (Ksolo !== null && Ksolo >= 0) {
    const fK   = faixaPotassio(Ksolo);
    const dk   = fK.dose;
    const kgK  = dk * areaHa;
    const sacK = Math.ceil(ajustarSacosMinimos(kgK / 50));
    let custoStr = '';
    if (temPreco && pPrecoK !== null && sacK > 0) {
      const custo = sacK * pPrecoK;
      custoTotal += custo;
      temCusto = true;
      custoStr = `<div class="plj-card-custo">💰 ${fmt(sacK,0)} sacos × ${moeda.format(pPrecoK)} = <strong>${moeda.format(custo)}</strong></div>`;
    }
    insumoCards.push(kgK === 0
      ? `<div class="plj-card sem-correcao">
          <span class="plj-card-icone">🟠</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Potássio (K₂O)</div>
            <div class="plj-card-detalhe">Solo ${fK.label} — sem necessidade de correção</div>
          </div>
          <div class="plj-card-qty"><span class="plj-card-qty-val">—</span></div>
         </div>`
      : `<div class="plj-card">
          <span class="plj-card-icone">🟠</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Potássio (K₂O)</div>
            <div class="plj-card-detalhe">Solo ${fK.label} → dose ${dk} kg/ha · ${fmt(kgK,1)} kg total${custoStr}</div>
          </div>
          <div class="plj-card-qty">
            <span class="plj-card-qty-val">${sacK}</span>
            <span class="plj-card-qty-unit">sacos 50 kg</span>
          </div>
         </div>`);
  }

  // Nitrogênio
  if (A > 0) {
    // Ajuste por MO: se MO > 3.5% reduz 10 kg/ha (N mineralizado)
    let dn = doseNInput !== null ? doseNInput : 30;
    let origemN = doseNInput !== null ? 'informada' : 'padrão';
    let ajusteN = '';
    if (MO !== null && MO > 3.5 && doseNInput === null) {
      dn = Math.max(0, dn - 10);
      ajusteN = ` (−10 kg/ha por MO elevada: ${fmt(MO,1)}%)`;
    }
    const kgN  = dn * areaHa;
    const sacN = Math.ceil(ajustarSacosMinimos(kgN / 50));
    let custoStr = '';
    if (temPreco && pPrecoN !== null && sacN > 0) {
      const custo = sacN * pPrecoN;
      custoTotal += custo;
      temCusto = true;
      custoStr = `<div class="plj-card-custo">💰 ${fmt(sacN,0)} sacos × ${moeda.format(pPrecoN)} = <strong>${moeda.format(custo)}</strong></div>`;
    }
    insumoCards.push(kgN === 0
      ? `<div class="plj-card sem-correcao">
          <span class="plj-card-icone">🔵</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Nitrogênio (N)</div>
            <div class="plj-card-detalhe">Dose zero — sem necessidade de adubação nitrogenada</div>
          </div>
          <div class="plj-card-qty"><span class="plj-card-qty-val">—</span></div>
         </div>`
      : `<div class="plj-card">
          <span class="plj-card-icone">🔵</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Nitrogênio (N)</div>
            <div class="plj-card-detalhe">Dose ${origemN}: ${fmt(dn,1)} kg/ha${ajusteN} · ${fmt(kgN,1)} kg total${custoStr}</div>
          </div>
          <div class="plj-card-qty">
            <span class="plj-card-qty-val">${sacN}</span>
            <span class="plj-card-qty-unit">sacos 50 kg</span>
          </div>
         </div>`);
  }

  // Calcário
  if (V1 !== null && T !== null && V1 >= 0 && T >= 0) {
    if (PRNT <= 0) {
      insumoCards.push(`<div class="plj-card plj-card-aviso">
          <span class="plj-card-icone">⚠️</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Calcário</div>
            <div class="plj-card-detalhe">Informe o PRNT do calcário (valor deve ser maior que 0%) para calcular a necessidade de calagem.</div>
          </div>
          <div class="plj-card-qty"><span class="plj-card-qty-val">—</span></div>
         </div>`);
    } else {
    const nc      = V1 < 60 ? ((60 - V1) * T) / PRNT : 0;
    const kgCal   = nc * areaHa * 1000;
    const sacCal  = Math.ceil(ajustarSacosMinimos(kgCal / 50));
    let custoStr = '';
    if (temPreco && pPrecoC !== null && sacCal > 0) {
      const custo = sacCal * pPrecoC;
      custoTotal += custo;
      temCusto = true;
      custoStr = `<div class="plj-card-custo">💰 ${fmt(sacCal,0)} sacos × ${moeda.format(pPrecoC)} = <strong>${moeda.format(custo)}</strong></div>`;
    }
    const fV = faixaSaturacao(V1);
    insumoCards.push(kgCal === 0
      ? `<div class="plj-card sem-correcao">
          <span class="plj-card-icone">⚪</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Calcário</div>
            <div class="plj-card-detalhe">${V1 >= 60 ? 'V% já ≥ 60% — sem necessidade de calagem' : 'CTC = 0 — sem necessidade de calagem calculável'}</div>
          </div>
          <div class="plj-card-qty"><span class="plj-card-qty-val">—</span></div>
         </div>`
      : `<div class="plj-card">
          <span class="plj-card-icone">⚪</span>
          <div class="plj-card-info">
            <div class="plj-card-nome">Calcário (PRNT ${fmt(PRNT,0)}%)</div>
            <div class="plj-card-detalhe">V1=${fmt(V1,1)}% → meta 60% · NC=${fmt(nc,2)} t/ha · ${fmt(kgCal,1)} kg total${custoStr}</div>
          </div>
          <div class="plj-card-qty">
            <span class="plj-card-qty-val">${sacCal}</span>
            <span class="plj-card-qty-unit">sacos 50 kg</span>
          </div>
         </div>`);
    } // end else (PRNT > 0)
  }

  if (insumoCards.length > 0) {
    html += `
      <div style="margin-top:18px;">
        <div class="plj-resultado-titulo">🚜 Necessidade de Insumos</div>
        <div class="plj-cards">${insumoCards.join('')}</div>
        ${temCusto ? `
        <div class="plj-custo-total">
          <span class="plj-custo-total-label">💰 Custo Total Estimado dos Insumos</span>
          <span class="plj-custo-total-val">${moeda.format(custoTotal)}</span>
        </div>` : ''}
      </div>`;
  }

  html += `
    <p style="font-size:0.74rem; color:rgba(255,255,255,0.35); margin-top:14px;">
      * Resultados calculados apenas com os campos preenchidos. Consulte um agrônomo para recomendações precisas.
    </p>`;

  resultado.innerHTML = html;
  resultado.style.display = 'block';
  resultado.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

window.calcular = calcular;

/* ── Listeners ─────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Botão calcular
  const btn = document.getElementById('botao-calcular');
  if (btn) btn.addEventListener('click', calcular);

  // Preview em tempo real
  ['id_area', 'id_linhas', 'id_plantas'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', atualizarPreviewPlantio);
  });

  // Indicadores de faixa
  ['id_fosforo', 'id_potassio', 'id_saturacao'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', atualizarFaixas);
  });

  // Init
  atualizarPreviewPlantio();
  atualizarFaixas();
});