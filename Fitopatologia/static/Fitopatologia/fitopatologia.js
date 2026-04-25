// Informações detalhadas sobre cada doença
const diseaseInfo = {
    antracnose: {
        title: 'Antracnose',
        description: '<h3>Descrição</h3><p>A antracnose é uma doença fúngica que afeta principalmente as folhas e raízes da mandioca, causando lesões necróticas e podendo levar a perdas significativas na produção.</p><h3>Sintomas</h3><ul><li>Manchas escuras e afundadas nas folhas</li><li>Lesões alongadas nos caules</li><li>Podridão nas raízes tuberosas</li><li>Desfolha prematura</li></ul><h3>Condições Favoráveis</h3><ul><li>Alta umidade relativa do ar</li><li>Temperaturas entre 20-28°C</li><li>Ferimentos nas plantas</li></ul><h3>Controle</h3><ul><li>Usar cultivares resistentes</li><li>Aplicar fungicidas preventivos</li><li>Melhorar drenagem do solo</li><li>Eliminar plantas infectadas</li></ul>'
    },
    oidio: {
        title: 'Oídio',
        description: '<h3>Descrição</h3><p>O oídio é uma doença fúngica que forma um pó branco nas superfícies foliares, reduzindo a capacidade fotossintética e o desenvolvimento da planta.</p><h3>Sintomas</h3><ul><li>Pó branco nas folhas (face superior e inferior)</li><li>Folhas com aspecto empoeirado</li><li>Deformação e ressecamento das folhas</li><li>Redução do crescimento</li></ul><h3>Condições Favoráveis</h3><ul><li>Clima seco com umidade moderada</li><li>Temperaturas entre 15-25°C</li><li>Ventilação inadequada</li></ul><h3>Controle</h3><ul><li>Aplicar enxofre em pó</li><li>Usar fungicidas específicos</li><li>Melhorar ventilação entre plantas</li><li>Evitar sombreamento excessivo</li></ul>'
    },
    'podridao-radicular': {
        title: 'Podridão Radicular',
        description: '<h3>Descrição</h3><p>A podridão radicular é uma doença causada por fungos do solo que atacam as raízes e tubérculos, ocasionando apodrecimento e morte prematura da planta.</p><h3>Sintomas</h3><ul><li>Murcha da parte aérea</li><li>Raízes com coloração escura e mole</li><li>Odor desagradável nas raízes</li><li>Morte da planta</li></ul><h3>Condições Favoráveis</h3><ul><li>Solo excessivamente úmido</li><li>Drenagem deficiente</li><li>Solos compactados</li><li>Temperaturas elevadas</li></ul><h3>Controle</h3><ul><li>Melhorar drenagem superior</li><li>Usar sementes de boa qualidade</li><li>Aplicar fungicidas ao solo</li><li>Rotação de culturas</li></ul>'
    },
    ferrugem: {
        title: 'Ferrugem',
        description: '<h3>Descrição</h3><p>A ferrugem é uma doença fúngica que forma pústulas avermelhadas nas folhas, reduzindo a capacidade fotossintética e o desenvolvimento da planta.</p><h3>Sintomas</h3><ul><li>Pústulas avermelhadas nas folhas</li><li>Descoloração ao redor das lesões</li><li>Folhas secas e caídas</li><li>Redução de crescimento</li></ul><h3>Condições Favoráveis</h3><ul><li>Clima quente e úmido</li><li>Temperaturas entre 15-25°C</li><li>Presença de orvalho</li></ul><h3>Controle</h3><ul><li>Usar cultivares resistentes</li><li>Aplicar fungicidas protetor</li><li>Remover folhas infectadas</li><li>Melhorar ventilação</li></ul>'
    },
    bacteriose: {
        title: 'Bacteriose',
        description: '<h3>Descrição</h3><p>A bacteriose é uma doença bacteriana que afeta principalmente as folhas e caules, causando lesões aquosas e destruição dos tecidos vegetais.</p><h3>Sintomas</h3><ul><li>Lesões aquosas nas folhas</li><li>Queimadura das bordas das folhas</li><li>Cancrinha nos caules</li><li>Murchamento generalizado</li></ul><h3>Condições Favoráveis</h3><ul><li>Alta umidade</li><li>Temperaturas entre 25-30°C</li><li>Presença de ferimentos nas plantas</li><li>Irrigação por aspersão</li></ul><h3>Controle</h3><ul><li>Evitar ferimentos nas plantas</li><li>Usar material de propagação sadio</li><li>Remover plantas infectadas</li><li>Bactericidas à base de cobre</li></ul>'
    },
    'mancha-bacteriana': {
        title: 'Mancha Bacteriana',
        description: '<h3>Descrição</h3><p>A mancha bacteriana é uma doença bacteriana que forma manchas oleosas nas folhas, causando desfolha e redução significativa da produção.</p><h3>Sintomas</h3><ul><li>Manchas oleosas com halo amarelo</li><li>Lesões escuras e encharcadas</li><li>Desfolha progressiva</li><li>Redução de vigor</li></ul><h3>Condições Favoráveis</h3><ul><li>Clima quente e úmido</li><li>Orvalho prolongado</li><li>Ferimentos nas folhas</li></ul><h3>Controle</h3><ul><li>Usar cultivares tolerantes</li><li>Bactericidas preventivos</li><li>Eliminar folhas infectadas</li><li>Melhorar espaçamento entre plantas</li></ul>'
    },
    'apodrecimento-bacteriano': {
        title: 'Apodrecimento Bacteriano',
        description: '<h3>Descrição</h3><p>O apodrecimento bacteriano afeta principalmente as raízes tuberosas durante o armazenamento ou em campo, causando perda total da produção.</p><h3>Sintomas</h3><ul><li>Podridão mole nas raízes</li><li>Odor fétido característico</li><li>Exsudato bacteriano</li><li>Apodrecimento rápido</li></ul><h3>Condições Favoráveis</h3><ul><li>Umidade relativa alta</li><li>Temperaturas entre 25-35°C</li><li>Ferimentos nas raízes</li><li>Armazenamento inadequado</li></ul><h3>Controle</h3><ul><li>Coleita cuidadosa evitando ferimentos</li><li>Armazenamento em local fresco e seco</li><li>Usar material sadio para plantio</li><li>Bom ventiação durante armazenamento</li></ul>'
    }
};

// Elementos do DOM
const modal = document.getElementById('diseaseModal');
const modalTitle = document.getElementById('diseaseModalTitle');
const modalBody = document.getElementById('diseaseModalBody');
const closeBtn = document.querySelector('.disease-modal-close');
const diseaseCards = document.querySelectorAll('.disease-card');

// Event listeners para os cards
diseaseCards.forEach(card => {
    card.addEventListener('click', function() {
        const diseaseKey = this.dataset.disease;
        const disease = diseaseInfo[diseaseKey];
        
        if (disease) {
            modalTitle.textContent = disease.title;
            modalBody.innerHTML = disease.description;
            modal.style.display = 'block';
        }
    });
});

// Fechar modal ao clicar no X
closeBtn.addEventListener('click', function() {
    modal.style.display = 'none';
});

// Fechar modal ao clicar fora do conteúdo
window.addEventListener('click', function(e) {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Fechar modal com ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        modal.style.display = 'none';
    }
});
