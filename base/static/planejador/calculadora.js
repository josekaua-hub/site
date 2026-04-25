const moedaBRL = new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
});

function lerNumero(idCampo, valorPadrao = null) {
    const campo = document.getElementById(idCampo);

    if (!campo) {
        return valorPadrao;
    }

    const valorBruto = campo.value.trim().replace(',', '.');

    if (valorBruto === '') {
        return valorPadrao;
    }

    const valor = Number.parseFloat(valorBruto);
    return Number.isNaN(valor) ? valorPadrao : valor;
}

function formatarNumero(valor) {
    return valor.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function obterPrecoInsumo(precoEspecifico, precoGeral) {
    if (precoEspecifico !== null) {
        return precoEspecifico;
    }
    return precoGeral;
}

function ajustarSacosMinimos(sacosCalculados) {
    if (sacosCalculados > 0 && sacosCalculados < 1) {
        return 1;
    }
    return sacosCalculados;
}

function calcular() {
    console.log('Iniciando cálculo...');
    // Captura de valores
    let A = lerNumero('id_area');
    let L = lerNumero('id_linhas', 1.0);
    let P = lerNumero('id_plantas', 0.8);
    let Psolo = lerNumero('id_fosforo');
    let Ksolo = lerNumero('id_potassio');
    let doseNitrogenioInformada = lerNumero('id_nitrogenio');
    let MO = lerNumero('id_materia');
    let V1 = lerNumero('id_saturacao');
    let T = lerNumero('id_ctc');
    let PRNT = lerNumero('id_calcario', 80);
    let quantidade = lerNumero('id_quantidade');
    let preco = lerNumero('id_preco');
    let precoFosforo = lerNumero('id_preco_fosforo');
    let precoPotassio = lerNumero('id_preco_potassio');
    let precoNitrogenio = lerNumero('id_preco_nitrogenio');
    let precoCalcario = lerNumero('id_preco_calcario');
    let quantidadeInformada = quantidade !== null;
    let precoInformado = preco !== null;
    let calcularCustoRecomendado = (
        precoInformado ||
        precoFosforo !== null ||
        precoPotassio !== null ||
        precoNitrogenio !== null ||
        precoCalcario !== null
    );

    console.log('Valores capturados:', {
        A, L, P, Psolo, Ksolo, doseNitrogenioInformada, MO, V1, T, PRNT,
        quantidade, preco, precoFosforo, precoPotassio, precoNitrogenio, precoCalcario
    });

    let plantioHtml = '';
    let insumosHtml = '';
    let custosHtml = '';
    let secoesCusto = [];
    let linhasCustoInsumos = [];
    let custoTotalInsumos = 0;
    let covas = 0;
    let areaHa = 0;

    if (
        (quantidadeInformada && quantidade < 0) ||
        (precoInformado && preco < 0) ||
        (precoFosforo !== null && precoFosforo < 0) ||
        (precoPotassio !== null && precoPotassio < 0) ||
        (precoNitrogenio !== null && precoNitrogenio < 0) ||
        (precoCalcario !== null && precoCalcario < 0)
    ) {
        custosHtml = '<p style="color:red;"><strong>Erro no custo:</strong> quantidade e preço não podem ser negativos.</p>';
    } else if (quantidadeInformada && !precoInformado) {
        custosHtml = '<p style="color:red;"><strong>Erro no custo:</strong> informe o preço por saco para calcular o valor da quantidade informada.</p>';
    } else if (quantidadeInformada && precoInformado) {
        let custoTotal = quantidade * preco;
        secoesCusto.push(`
            <h3>💰 Custo dos Insumos</h3>
            <p><strong>Quantidade informada:</strong> ${formatarNumero(quantidade)} sacos</p>
            <p><strong>Preço por saco:</strong> ${moedaBRL.format(preco)}</p>
            <p><strong>Custo estimado:</strong> ${moedaBRL.format(custoTotal)}</p>
        `);
    }

    if ((!A || A <= 0) && !custosHtml) {
        console.log('Erro: Área inválida');
        document.getElementById('plantio').innerHTML = '<p style="color:red;"><strong>Erro:</strong> A area e obrigatoria e deve ser maior que 0.</p>';
        document.getElementById('insumos').innerHTML = '';
        document.getElementById('custos').innerHTML = '';
        document.getElementById('resultado').style.display = 'block';
        return;
    }

    if (doseNitrogenioInformada !== null && doseNitrogenioInformada < 0) {
        document.getElementById('plantio').innerHTML = '';
        document.getElementById('insumos').innerHTML = '<p style="color:red;"><strong>Erro:</strong> a dose de Nitrogênio deve ser maior ou igual a 0.</p>';
        document.getElementById('custos').innerHTML = '';
        document.getElementById('resultado').style.display = 'block';
        return;
    }

    if (A && A > 0) {
        areaHa = A / 10000;
        covas = Math.ceil((A / (L * P)) * 1.1);
        let varas = Math.ceil(covas / 5);
        plantioHtml = `
            <h3>🌱 Plantio e Mudas</h3>
            <p><strong>Total de Covas:</strong> ${covas} manivas</p>
            <p><strong>Total de Varas:</strong> ${varas} varas</p>
        `;
        console.log('Plantio calculado:', {covas, varas});
    }

    // calculo do fosforo (dose em kg/ha)

    if (Psolo !== null && Psolo >= 0) {
        let dp = Psolo <= 10 ? 60 : Psolo <= 20 ? 40 : 20;
        let kg_p = dp * areaHa;
        let sacos_p = Math.ceil(ajustarSacosMinimos(kg_p / 50.0));
        if (kg_p === 0) {
            insumosHtml += `<p><strong>Fósforo (P₂O₅):</strong> sem necessidade de correção para este solo.</p>`;
        } else {
            insumosHtml += `<p><strong>Fósforo (P₂O₅):</strong> ${kg_p.toFixed(1)} kg (${sacos_p} sacos de 50kg)</p>`;
        }
        if (calcularCustoRecomendado && sacos_p > 0) {
            let precoFosforoUsado = obterPrecoInsumo(precoFosforo, preco);
            if (precoFosforoUsado !== null) {
                let custoFosfatado = sacos_p * precoFosforoUsado;
                custoTotalInsumos += custoFosfatado;
                linhasCustoInsumos.push(`<p><strong>Fósforo (P₂O₅):</strong> ${formatarNumero(sacos_p)} sacos × ${moedaBRL.format(precoFosforoUsado)} = ${moedaBRL.format(custoFosfatado)}</p>`);
            }
        }
        console.log('Fósforo calculado:', {dp, areaHa, kg_p, sacos_p});
    }

    // calculo do potassio (dose em kg/ha)

    if (Ksolo !== null && Ksolo >= 0) {
        let dk;
        if (Ksolo <= 0.05) {
            dk = 40;  // 0 - 0.05
        } else if (Ksolo <= 0.10) {
            dk = 30;  // 0.06 - 0.10
        } else if (Ksolo <= 0.15) {
            dk = 20;  // 0.11 - 0.15
        } else {
            dk = 0;   // > 0.15
        }
        let kg_k = dk * areaHa;
        let sacos_k = Math.ceil(ajustarSacosMinimos(kg_k / 50.0));
        if (kg_k === 0) {
            insumosHtml += `<p><strong>Potássio (K₂O):</strong> sem necessidade de correção para este solo.</p>`;
        } else {
            insumosHtml += `<p><strong>Potássio (K₂O):</strong> ${kg_k.toFixed(1)} kg (${sacos_k} sacos de 50kg)</p>`;
        }
        if (calcularCustoRecomendado && sacos_k > 0) {
            let precoPotassioUsado = obterPrecoInsumo(precoPotassio, preco);
            if (precoPotassioUsado !== null) {
                let custoPotassico = sacos_k * precoPotassioUsado;
                custoTotalInsumos += custoPotassico;
                linhasCustoInsumos.push(`<p><strong>Potássio (K₂O):</strong> ${formatarNumero(sacos_k)} sacos × ${moedaBRL.format(precoPotassioUsado)} = ${moedaBRL.format(custoPotassico)}</p>`);
            }
        }
        console.log('Potássio calculado:', {dk, areaHa, kg_k, sacos_k});
    }

    // calculo do nitrogenio (dose em kg/ha)

    if (A && A > 0) {
        let dn = doseNitrogenioInformada === null ? 30 : doseNitrogenioInformada;
        let origemDoseN = doseNitrogenioInformada === null ? 'padrão' : 'informada';
        let kg_n = dn * areaHa;
        let sacos_n = Math.ceil(ajustarSacosMinimos(kg_n / 50.0));
        if (kg_n === 0) {
            insumosHtml += `<p><strong>Nitrogênio (N):</strong> sem necessidade de adubação nitrogenada.</p>`;
        } else {
            insumosHtml += `<p><strong>Nitrogênio (N):</strong> ${kg_n.toFixed(1)} kg (${sacos_n} sacos de 50kg) - dose ${origemDoseN} de ${dn.toFixed(1)} kg/ha</p>`;
        }
        if (calcularCustoRecomendado && sacos_n > 0) {
            let precoNitrogenioUsado = obterPrecoInsumo(precoNitrogenio, preco);
            if (precoNitrogenioUsado !== null) {
                let custoNitrogenado = sacos_n * precoNitrogenioUsado;
                custoTotalInsumos += custoNitrogenado;
                linhasCustoInsumos.push(`<p><strong>Nitrogênio (N):</strong> ${formatarNumero(sacos_n)} sacos × ${moedaBRL.format(precoNitrogenioUsado)} = ${moedaBRL.format(custoNitrogenado)}</p>`);
            }
        }
        console.log('Nitrogênio calculado:', {areaHa, dn, origemDoseN, kg_n, sacos_n});
    }

    //calculo do calcario
    if (V1 !== null && T !== null && A !== null && A > 0 && V1 >= 0 && T >= 0) {
        let nc = V1 < 60 ? ((60 - V1) * T) / PRNT : 0;
        let total_t = nc * (A / 10000);
        let kg_calcario = total_t * 1000;
        let sacos_calcario = Math.ceil(ajustarSacosMinimos(kg_calcario / 50));
        if (kg_calcario === 0) {
            insumosHtml += `<p><strong>Calcário:</strong> sem necessidade de correção (V% já ≥ 60%).</p>`;
        } else {
            insumosHtml += `<p><strong>Calcário:</strong> ${kg_calcario.toFixed(1)} kg (${sacos_calcario} sacos de 50kg)</p>`;
        }
        if (calcularCustoRecomendado && sacos_calcario > 0) {
            let precoCalcarioUsado = obterPrecoInsumo(precoCalcario, preco);
            if (precoCalcarioUsado !== null) {
                let custoCalcario = sacos_calcario * precoCalcarioUsado;
                custoTotalInsumos += custoCalcario;
                linhasCustoInsumos.push(`<p><strong>Calcário:</strong> ${formatarNumero(sacos_calcario)} sacos × ${moedaBRL.format(precoCalcarioUsado)} = ${moedaBRL.format(custoCalcario)}</p>`);
            }
        }
        console.log('Calcário calculado:', {nc, total_t, kg_calcario, sacos_calcario});
    }

    if (calcularCustoRecomendado && !custosHtml && linhasCustoInsumos.length > 0) {
        secoesCusto.push(`
            <h3>💰 Custo dos Insumos Recomendados</h3>
            ${linhasCustoInsumos.join('')}
            <p><strong>Total estimado:</strong> ${moedaBRL.format(custoTotalInsumos)}</p>
        `);
    }

    if (!custosHtml) {
        custosHtml = secoesCusto.join('');
    }

    console.log('HTML gerado:', {plantioHtml, insumosHtml});

    if (plantioHtml || insumosHtml) {
        if (insumosHtml) insumosHtml = '<h3>🚜 Necessidade de Insumos</h3>' + insumosHtml;
        document.getElementById('plantio').innerHTML = plantioHtml;
        document.getElementById('insumos').innerHTML = insumosHtml;
        document.getElementById('custos').innerHTML = custosHtml;
        document.getElementById('resultado').style.display = 'block';
        console.log('Resultado exibido');
    } else if (custosHtml) {
        document.getElementById('plantio').innerHTML = '';
        document.getElementById('insumos').innerHTML = '';
        document.getElementById('custos').innerHTML = custosHtml;
        document.getElementById('resultado').style.display = 'block';
        console.log('Resultado de custo exibido');
    } else {
        document.getElementById('resultado').style.display = 'none';
        console.log('Resultado oculto');
    }
    console.log('Cálculo finalizado');
}

window.calcular = calcular;

document.addEventListener('DOMContentLoaded', () => {
    const botaoCalcular = document.getElementById('botao-calcular');

    if (botaoCalcular) {
        botaoCalcular.addEventListener('click', calcular);
    }
});