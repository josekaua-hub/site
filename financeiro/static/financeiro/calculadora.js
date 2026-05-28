function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

function parseNumber(value) {
    if (value === null || value === undefined) return 0;

    let normalized = String(value).trim().replace(/\s+/g, '');
    if (normalized === '') return 0;

    const hasComma = normalized.indexOf(',') !== -1;
    const hasDot = normalized.indexOf('.') !== -1;

    if (hasComma) {
        // Formato brasileiro: 1.234,56 ou 1234,56
        normalized = normalized.replace(/\./g, '').replace(/,/g, '.');
    } else if (hasDot) {
        const dotCount = (normalized.match(/\./g) || []).length;
        if (dotCount > 1) {
            // Múltiplos pontos => separadores de milhar
            normalized = normalized.replace(/\./g, '');
        } else {
            const parts = normalized.split('.');
            if (parts[1] && parts[1].length <= 2) {
                // Um ponto e até duas casas decimais => pode ser decimal
                normalized = normalized;
            } else {
                // Um ponto e mais de duas casas => pode ser separador de milhar
                normalized = normalized.replace(/\./g, '');
            }
        }
    }

    normalized = normalized.replace(/[^0-9.\-]/g, '');
    const result = parseFloat(normalized);
    return Number.isNaN(result) ? 0 : result;
}

function calcularFinanceiro() {
    // Capturar dados de entrada
    const qtdProduzida = parseNumber(document.getElementById('qtdProduzida').value);
    const precoUnitario = parseNumber(document.getElementById('precoUnitario').value);
    
    // Custos Variáveis
    const custoSementes = parseNumber(document.getElementById('custoSementes').value);
    const custoAdubo = parseNumber(document.getElementById('custoAdubo').value);
    const custoDefensivos = parseNumber(document.getElementById('custoDefensivos').value);
    const custoAgua = parseNumber(document.getElementById('custoAgua').value);
    const custoMaoObra = parseNumber(document.getElementById('custoMaoObra').value);
    const custoEnergia = parseNumber(document.getElementById('custoEnergia').value);
    const custoColheita = parseNumber(document.getElementById('custoColheita').value);
    const custoTransporte = parseNumber(document.getElementById('custoTransporte').value);
    
    // Custos Fixos
    const custoAluguel = parseNumber(document.getElementById('custoAluguel').value);
    const custoManutencao = parseNumber(document.getElementById('custoManutencao').value);
    const ciclosPorAno = parseNumber(document.getElementById('ciclosPorAno').value) || 1;
    
    // Cálculos
    const receitaTotal = qtdProduzida * precoUnitario;
    
    const custosVariaveis = custoSementes + custoAdubo + custoDefensivos + custoAgua + 
                           custoMaoObra + custoEnergia + custoColheita + custoTransporte;
    
    const custosFixosAnual = custoAluguel + custoManutencao;
    const custosFixosCiclo = custosFixosAnual / ciclosPorAno;
    
    const custoTotalCiclo = custosVariaveis + custosFixosCiclo;
    const saldoFinal = receitaTotal - custoTotalCiclo;
    
    const margemLucro = receitaTotal > 0 ? ((saldoFinal / receitaTotal) * 100) : 0;
    const roi = custoTotalCiclo > 0 ? ((saldoFinal / custoTotalCiclo) * 100) : 0;
    
    const custoUnitario = qtdProduzida > 0 ? (custoTotalCiclo / qtdProduzida) : 0;
    const lucroUnitario = precoUnitario - custoUnitario;
    
    const pontoEquilibrio = precoUnitario > custoUnitario ? 
                           (custosFixosCiclo / (precoUnitario - custoUnitario)) : 0;
    const pontoEquilibrioValor = pontoEquilibrio * precoUnitario;
    
    // Atualizar UI
    document.getElementById('receitaTotal').textContent = formatarMoeda(receitaTotal);
    document.getElementById('custoTotal').textContent = formatarMoeda(custoTotalCiclo);
    document.getElementById('saldoFinal').textContent = formatarMoeda(saldoFinal);
    
    // Atualizar cor do saldo
    const saldoAlert = document.getElementById('saldoAlert');
    saldoAlert.classList.remove('positivo', 'negativo');
    if (saldoFinal >= 0) {
        saldoAlert.classList.add('positivo');
    } else {
        saldoAlert.classList.add('negativo');
    }
    
    document.getElementById('margemLucro').innerHTML = `<strong>${margemLucro.toFixed(2)}%</strong>`;
    document.getElementById('roi').innerHTML = `<strong>${roi.toFixed(2)}%</strong>`;
    document.getElementById('custoUnitario').innerHTML = `<strong>${formatarMoeda(custoUnitario)}</strong>`;
    document.getElementById('lucroUnitario').innerHTML = `<strong>${formatarMoeda(lucroUnitario)}</strong>`;
    document.getElementById('pontoEquilibrio').innerHTML = `<strong>${Math.ceil(pontoEquilibrio)} unidades</strong>`;
    document.getElementById('pontoEquilibrioValor').innerHTML = `<strong>${formatarMoeda(pontoEquilibrioValor)}</strong>`;
    
    document.getElementById('custosVariaveis').textContent = formatarMoeda(custosVariaveis);
    document.getElementById('custosFixosCiclo').textContent = formatarMoeda(custosFixosCiclo);
    document.getElementById('custoTotalCiclo').textContent = formatarMoeda(custoTotalCiclo);
}

function calcularCenario() {
    const qtdProduzida = parseNumber(document.getElementById('qtdProduzida').value);
    const precoUnitario = parseNumber(document.getElementById('precoUnitario').value);
    const variacaoPreco = parseNumber(document.getElementById('variacaoPreco').value);
    const variacaoQtd = parseNumber(document.getElementById('variacaoQtd').value);
    
    const novoPreco = precoUnitario * (1 + variacaoPreco / 100);
    const novaQtd = qtdProduzida * (1 + variacaoQtd / 100);
    
    // Custos (permanecem iguais)
    const custoSementes = parseNumber(document.getElementById('custoSementes').value);
    const custoAdubo = parseNumber(document.getElementById('custoAdubo').value);
    const custoDefensivos = parseNumber(document.getElementById('custoDefensivos').value);
    const custoAgua = parseNumber(document.getElementById('custoAgua').value);
    const custoMaoObra = parseNumber(document.getElementById('custoMaoObra').value);
    const custoEnergia = parseNumber(document.getElementById('custoEnergia').value);
    const custoColheita = parseNumber(document.getElementById('custoColheita').value);
    const custoTransporte = parseNumber(document.getElementById('custoTransporte').value);
    const custoAluguel = parseNumber(document.getElementById('custoAluguel').value);
    const custoManutencao = parseNumber(document.getElementById('custoManutencao').value);
    const ciclosPorAno = parseNumber(document.getElementById('ciclosPorAno').value) || 1;
    
    const custosVariaveis = custoSementes + custoAdubo + custoDefensivos + custoAgua + 
                           custoMaoObra + custoEnergia + custoColheita + custoTransporte;
    const custosFixosCiclo = (custoAluguel + custoManutencao) / ciclosPorAno;
    const custoTotal = custosVariaveis + custosFixosCiclo;
    
    const novaReceita = novaQtd * novoPreco;
    const novoSaldo = novaReceita - custoTotal;
    
    document.getElementById('novoPreco').textContent = formatarMoeda(novoPreco);
    document.getElementById('novaQtd').textContent = `${novaQtd.toFixed(2)} unidades`;
    document.getElementById('novoSaldo').textContent = formatarMoeda(novoSaldo);
    
    // Atualizar cor
    const novoSaldoAlert = document.getElementById('novoSaldoAlert');
    novoSaldoAlert.classList.remove('positivo', 'negativo');
    if (novoSaldo >= 0) {
        novoSaldoAlert.classList.add('positivo');
    } else {
        novoSaldoAlert.classList.add('negativo');
    }
    
    document.getElementById('resultadosCenario').style.display = 'block';
}

function limparFormulario() {
    // Resetar campos
    document.getElementById('qtdProduzida').value = '1000';
    document.getElementById('precoUnitario').value = '2.50';
    document.getElementById('custoSementes').value = '200';
    document.getElementById('custoAdubo').value = '300';
    document.getElementById('custoDefensivos').value = '150';
    document.getElementById('custoAgua').value = '100';
    document.getElementById('custoMaoObra').value = '250';
    document.getElementById('custoEnergia').value = '100';
    document.getElementById('custoColheita').value = '200';
    document.getElementById('custoTransporte').value = '150';
    document.getElementById('custoAluguel').value = '0';
    document.getElementById('custoManutencao').value = '0';
    document.getElementById('ciclosPorAno').value = '2';
    document.getElementById('variacaoPreco').value = '0';
    document.getElementById('variacaoQtd').value = '0';
    document.getElementById('resultadosCenario').style.display = 'none';
    
    // Limpar resultados
    calcularFinanceiro();
}

function submitSaveFixos(){
    const aluguel = document.getElementById('custoAluguel').value || 0;
    const manut = document.getElementById('custoManutencao').value || 0;
    const form = document.getElementById('saveFixosForm');
    if (!form) return;
    const hiddenAluguel = document.getElementById('hiddenCustoAluguel');
    const hiddenManut = document.getElementById('hiddenCustoManutencao');
    if (hiddenAluguel) hiddenAluguel.value = aluguel;
    if (hiddenManut) hiddenManut.value = manut;
    form.submit();
}

function formatInputValue(input) {
    if (!input) return;
    const value = input.value;
    if (!value) return;
    const numeric = parseNumber(value);
    if (numeric === 0 && !/[0-9]/.test(value)) {
        input.value = '';
        return;
    }
    input.value = formatBr(numeric, value);
}

function unformatInputValue(input) {
    if (!input) return;
    const value = input.value;
    if (!value) return;
    const numeric = parseNumber(value);
    input.value = numeric === 0 && !/[0-9]/.test(value) ? '' : String(numeric);
}

function formatBr(value, originalValue) {
    if (value === null || value === undefined || Number.isNaN(value)) return '';
    const stringValue = String(value);
    const hasDecimal = String(originalValue).includes(',') || String(originalValue).includes('.');
    const options = {
        minimumFractionDigits: hasDecimal ? Math.max(String(originalValue).split(',')[1]?.length || 0, String(originalValue).split('.')[1]?.length || 0) : 0,
        maximumFractionDigits: 20,
    };
    return new Intl.NumberFormat('pt-BR', options).format(value);
}

function setupBrNumberFields() {
    const inputs = document.querySelectorAll('.br-number');
    inputs.forEach(input => {
        input.addEventListener('focus', () => unformatInputValue(input));
        input.addEventListener('blur', () => formatInputValue(input));
        if (input.value) {
            formatInputValue(input);
        }
    });
}

function setEditMode(enabled) {
    const inputs = document.querySelectorAll('.br-number');
    inputs.forEach(input => input.readOnly = !enabled);
    const editButton = document.getElementById('editButton');
    if (editButton) {
        editButton.textContent = enabled ? '🔒 Bloquear' : '✏️ Editar';
    }
}

function toggleEditMode() {
    const inputs = document.querySelectorAll('.br-number');
    if (!inputs.length) return;
    const currentlyReadOnly = inputs[0].readOnly;
    setEditMode(!currentlyReadOnly);
}

// Calcular ao carregar a página
window.addEventListener('load', function() {
    setupBrNumberFields();
    setEditMode(false);
    calcularFinanceiro();
});
