function calcular() {
    console.log('Iniciando cálculo...');
    // Captura de valores
    let A = parseFloat(document.getElementById('id_area').value) || null;
    let L = parseFloat(document.getElementById('id_linhas').value) || 1.0;
    let P = parseFloat(document.getElementById('id_plantas').value) || 0.8;
    let Psolo = parseFloat(document.getElementById('id_fosforo').value) || null;
    let Ksolo = parseFloat(document.getElementById('id_potassio').value) || null;
    let MO = parseFloat(document.getElementById('id_materia').value) || null;
    let V1 = parseFloat(document.getElementById('id_saturacao').value) || null;
    let T = parseFloat(document.getElementById('id_ctc').value) || null;
    let PRNT = parseFloat(document.getElementById('id_calcario').value) || 80;

    console.log('Valores capturados:', {A, L, P, Psolo, Ksolo, MO, V1, T, PRNT});

    // Validação: Área é obrigatória
    if (!A || A <= 0) {
        console.log('Erro: Área inválida');
        document.getElementById('plantio').innerHTML = '<p style="color:red;"><strong>Erro:</strong> A área é obrigatória e deve ser maior que 0.</p>';
        document.getElementById('insumos').innerHTML = '';
        document.getElementById('resultado').style.display = 'block';
        return;
    }

    let plantioHtml = '';
    let insumosHtml = '';
    let covas = 0;  

    if (A && A > 0) {
        covas = Math.ceil((A / (L * P)) * 1.1);
        let varas = Math.ceil(covas / 5);
        plantioHtml = `
            <h3>🌱 Plantio e Mudas</h3>
            <p><strong>Total de Covas:</strong> ${covas} manivas</p>
            <p><strong>Total de Varas:</strong> ${varas} varas</p>
        `;
        console.log('Plantio calculado:', {covas, varas});
    }

      //calculo do fosforo

    if (Psolo !== null && Psolo >= 0) {
        let dp = Psolo <= 10 ? 60 : Psolo <= 20 ? 40 : 20;
        let kg_p = (dp * covas) / 1000.0;
        let sacos_p = kg_p / 50.0;
        insumosHtml += `<p><strong>Adubo Fosfatado:</strong> ${kg_p.toFixed(1)} kg (${sacos_p.toFixed(1)} sacos de 50kg)</p>`;
        console.log('Fosfatado calculado:', {dp, kg_p, sacos_p});
    }

    //calculo do potassio

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
        let kg_k = (dk * covas) / 1000.0;
        let sacos_k = kg_k / 50.0;
        insumosHtml += `<p><strong>Adubo Potássico:</strong> ${kg_k.toFixed(1)} kg (${sacos_k.toFixed(1)} sacos de 50kg)</p>`;
        console.log('Potássico calculado:', {dk, kg_k, sacos_k});
    }

    //calculo do nitrogenio

    if (A && A > 0) {
        // Segundo a tabela, N é aplicado na cobertura com 30 kg/ha fixo
        let dn = 30;  // Fixo, independente de MO
        let kg_n = (dn * covas) / 1000.0;
        let sacos_n = kg_n / 50.0;
        insumosHtml += `<p><strong>Adubo Nitrogenado:</strong> ${kg_n.toFixed(1)} kg (${sacos_n.toFixed(1)} sacos de 50kg)</p>`;
        console.log('Nitrogenado calculado:', {dn, kg_n, sacos_n});
    }

    //calculo do calcario
    if (V1 !== null && T !== null && A !== null && A > 0 && V1 >= 0 && T >= 0) {
        let nc = V1 < 60 ? ((60 - V1) * T) / PRNT : 0;
        let total_t = nc * (A / 10000);
        let kg_calcario = total_t * 1000;
        let sacos_calcario = kg_calcario / 50;
        insumosHtml += `<p><strong>Calcário:</strong> ${kg_calcario.toFixed(1)} kg (${sacos_calcario.toFixed(1)} sacos de 50kg)</p>`;
        console.log('Calcário calculado:', {nc, total_t, kg_calcario, sacos_calcario});
    }

    console.log('HTML gerado:', {plantioHtml, insumosHtml});

    if (plantioHtml || insumosHtml) {
        if (insumosHtml) insumosHtml = '<h3>🚜 Necessidade de Insumos</h3>' + insumosHtml;
        document.getElementById('plantio').innerHTML = plantioHtml;
        document.getElementById('insumos').innerHTML = insumosHtml;
        document.getElementById('resultado').style.display = 'block';
        console.log('Resultado exibido');
    } else {
        document.getElementById('resultado').style.display = 'none';
        console.log('Resultado oculto');
    }
    console.log('Cálculo finalizado');
}