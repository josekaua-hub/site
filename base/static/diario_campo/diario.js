const mapaFieldsets = {
    preparo: 'preparo-solo',
    manejo: 'manejo-tratos',
    adubacao: 'adubacao-cobertura',
    tratamento: 'tratamento-fitossanitario',
    climatico: 'evento-climatico',
};

function atualizarFieldsets() {
    const valor = document.getElementById('tipo-atividade').value;

    Object.values(mapaFieldsets).forEach(function(id) {
        document.getElementById(id).style.display = 'none';
    });

    if (mapaFieldsets[valor]) {
        document.getElementById(mapaFieldsets[valor]).style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('tipo-atividade').addEventListener('change', atualizarFieldsets);

    // Preencher data de hoje automaticamente
    const campoData = document.getElementById('data');
    const hoje = new Date();
    const ano = hoje.getFullYear();
    const mes = String(hoje.getMonth() + 1).padStart(2, '0');
    const dia = String(hoje.getDate()).padStart(2, '0');
    campoData.value = `${ano}-${mes}-${dia}`;
});