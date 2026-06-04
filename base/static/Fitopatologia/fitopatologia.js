const diseaseInfo = {
    bacteriose: {
        title: 'Bacteriose da Mandioca',
        agente: 'Xanthomonas axonopodis pv. manihotis',
        description: '<h3>Descrição</h3><p>É a doença bacteriana mais importante da mandioca no Nordeste. Provoca queima das folhas, murcha e morte de ramos, sendo muito favorecida pelo clima quente e úmido do período chuvoso.</p><h3>Sintomas</h3><ul><li>Manchas aquosas nas folhas que rapidamente escurecem</li><li>Queima e seca nas bordas das folhas</li><li>Cancros nos caules com exsudato gomoso amarelado</li><li>Murcha e morte de ramos (murcha-do-topo)</li><li>Desfolha intensa nas épocas de chuva</li></ul><h3>Condições Favoráveis</h3><ul><li>Período chuvoso com alta umidade (&gt;80%)</li><li>Temperaturas entre 25–30 °C</li><li>Ferimentos nas plantas por insetos ou manuseio</li><li>Uso de manivas infectadas no plantio</li></ul><h3>Controle</h3><ul><li>Usar manivas-sementes certificadas e sadias</li><li>Evitar ferimentos durante tratos culturais</li><li>Remover e incinerar plantas e ramos infectados</li><li>Aplicar bactericidas à base de cobre preventivamente</li><li>Usar cultivares resistentes disponíveis pela Embrapa</li></ul>'
    },
    antracnose: {
        title: 'Antracnose',
        agente: 'Colletotrichum gloeosporioides',
        description: '<h3>Descrição</h3><p>Doença fúngica muito comum nas regiões produtoras do Nordeste, especialmente no período chuvoso. Ataca folhas, ramos e manivas, podendo comprometer o estande da lavoura quando o material de plantio está infectado.</p><h3>Sintomas</h3><ul><li>Manchas escuras e afundadas nas folhas e ramos jovens</li><li>Lesões alongadas nos caules com centro pálido e bordas escuras</li><li>Mumificação e morte de ponteiros</li><li>Podridão nas manivas durante o armazenamento</li><li>Desfolha prematura em ataques severos</li></ul><h3>Condições Favoráveis</h3><ul><li>Alta umidade relativa (&gt;80%) e chuvas frequentes</li><li>Temperaturas entre 20–28 °C</li><li>Ferimentos nas plantas</li><li>Plantio de manivas doentes</li></ul><h3>Controle</h3><ul><li>Tratar manivas com fungicidas antes do plantio</li><li>Usar cultivares resistentes</li><li>Aplicar fungicidas cúpricos ou sistêmicos preventivamente</li><li>Eliminar e incinerar ramos infectados</li><li>Melhorar drenagem e espaçamento entre plantas</li></ul>'
    },
    'podridao-radicular': {
        title: 'Podridão Radicular',
        agente: 'Phytophthora drechsleri / Fusarium spp.',
        description: '<h3>Descrição</h3><p>Complexo de doenças causado por fungos de solo que atacam as raízes tuberosas da mandioca. É um dos maiores problemas em áreas com solos mal drenados no Nordeste, causando perdas totais na produção.</p><h3>Sintomas</h3><ul><li>Murcha súbita da parte aérea sem causa aparente</li><li>Raízes com coloração escura (marrom a preta) e consistência mole</li><li>Odor desagradável nas raízes afetadas</li><li>Morte da planta em estádios avançados</li><li>Podridão que se espalha de raiz para raiz no solo</li></ul><h3>Condições Favoráveis</h3><ul><li>Solo encharcado ou com drenagem deficiente</li><li>Solos argilosos e compactados</li><li>Temperaturas elevadas associadas à umidade</li><li>Chuvas intensas seguidas de calor</li></ul><h3>Controle</h3><ul><li>Plantar em áreas com boa drenagem natural ou fazer camalhões</li><li>Usar manivas sadias e tratadas com fungicidas</li><li>Evitar compactação do solo</li><li>Fazer rotação de culturas</li><li>Retirar e eliminar plantas doentes do campo</li></ul>'
    },
    superalongamento: {
        title: 'Superalongamento dos Ramos',
        agente: 'Sphaceloma manihoticola',
        description: '<h3>Descrição</h3><p>Doença fúngica que causa deformações severas na parte aérea da mandioca, sendo frequentemente relatada em lavouras do Nordeste, especialmente em zonas de mata e agreste úmido. Pode causar perdas de até 80% em cultivares suscetíveis.</p><h3>Sintomas</h3><ul><li>Alongamento exagerado dos entrenós dos ramos (aspecto "estiolado")</li><li>Folhas pequenas, estreitas e deformadas no ápice</li><li>Bordas das folhas com manchas escuras e necróticas</li><li>Ramos quebradiços e com aspecto enfezado</li><li>Redução drástica da produção de raízes</li></ul><h3>Condições Favoráveis</h3><ul><li>Alta umidade e chuvas frequentes</li><li>Temperaturas amenas entre 18–24 °C</li><li>Ventos que facilitam a dispersão de esporos</li><li>Presença da doença em lavouras vizinhas</li></ul><h3>Controle</h3><ul><li>Usar cultivares resistentes (principal medida)</li><li>Evitar plantar em áreas com histórico da doença</li><li>Aplicar fungicidas sistêmicos preventivamente</li><li>Retirar e eliminar ponteiros infectados</li><li>Não usar manivas de plantas com sintomas</li></ul>'
    },
    cercosporiose: {
        title: 'Cercosporiose (Mancha Parda)',
        agente: 'Cercospora caribaea / C. henningsii',
        description: '<h3>Descrição</h3><p>Doença fúngica foliar muito comum em todo o Nordeste, ocorrendo praticamente em todas as lavouras de mandioca. Raramente causa perdas severas isoladamente, mas enfraquece a planta e favorece outras doenças.</p><h3>Sintomas</h3><ul><li>Manchas circulares a angulares de coloração parda ou marrom nas folhas</li><li>Halo amarelado ao redor das manchas</li><li>Centro das manchas com tonalidade mais clara e bordas escuras</li><li>Desfolha progressiva em ataques intensos</li><li>Redução da capacidade fotossintética</li></ul><h3>Condições Favoráveis</h3><ul><li>Períodos chuvosos prolongados</li><li>Alta umidade relativa do ar</li><li>Temperaturas entre 22–28 °C</li><li>Plantas com deficiência nutricional ou estresse hídrico</li></ul><h3>Controle</h3><ul><li>Manter nutrição adequada da lavoura</li><li>Evitar estresse hídrico com irrigação complementar</li><li>Aplicar fungicidas protetores (cúpricos, mancozebe) quando necessário</li><li>Usar cultivares com tolerância à doença</li><li>Eliminar restos culturais infectados após a colheita</li></ul>'
    }
};

// DOM
const modal = document.getElementById('diseaseModal');
const modalTitle = document.getElementById('diseaseModalTitle');
const modalBody = document.getElementById('diseaseModalBody');
const closeBtn = document.querySelector('.disease-modal-close');

document.querySelectorAll('.disease-card').forEach(card => {
    card.addEventListener('click', function() {
        const disease = diseaseInfo[this.dataset.disease];
        if (disease) {
            modalTitle.textContent = disease.title;
            modalBody.innerHTML =
                '<p class="disease-modal-agente">🔬 ' + disease.agente + '</p>' +
                disease.description;
            modal.style.display = 'block';
        }
    });
});

closeBtn.addEventListener('click', () => modal.style.display = 'none');
window.addEventListener('click', e => { if (e.target === modal) modal.style.display = 'none'; });
document.addEventListener('keydown', e => { if (e.key === 'Escape') modal.style.display = 'none'; });
