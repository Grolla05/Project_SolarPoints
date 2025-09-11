document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os elementos da interface de uma vez
    const applyButton = document.getElementById('applyFilterBtn');
    const restoreButton = document.getElementById('restoreFilterBtn');
    const minFlowInput = document.getElementById('minFlow');
    const maxFlowInput = document.getElementById('maxFlow');
    const quickFilterButtons = document.querySelectorAll('.quick-filter-btn'); // NOVO

    // Função centralizada para aplicar os filtros e recarregar a página
    const applyFilter = () => {
        const minFlow = minFlowInput.value;
        const maxFlow = maxFlowInput.value;
        
        const baseUrl = window.location.origin + window.location.pathname;
        const params = new URLSearchParams();

        if (minFlow) {
            params.append('minFlow', minFlow);
        }
        if (maxFlow) {
            params.append('maxFlow', maxFlow);
        }

        window.location.href = `${baseUrl}?${params.toString()}`;
    };
    
    // Lógica para o botão "Aplicar"
    if (applyButton) {
        applyButton.addEventListener('click', applyFilter);
    }

    // Lógica para o botão "Restaurar"
    if (restoreButton) {
        restoreButton.addEventListener('click', function() {
            const baseUrl = window.location.origin + window.location.pathname;
            window.location.href = baseUrl;
        });
    }

    // NOVO: Lógica para os botões de Filtros Rápidos
    if (quickFilterButtons) {
        quickFilterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // 1. Pega os valores min/max dos atributos 'data-' do botão clicado
                const min = this.getAttribute('data-min');
                const max = this.getAttribute('data-max');

                // 2. Preenche os campos de input com esses valores
                minFlowInput.value = min;
                maxFlowInput.value = max;

                // 3. Chama a função principal para aplicar o filtro
                applyFilter();
            });
        });
    }
});