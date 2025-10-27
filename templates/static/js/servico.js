// Fechar o modal se o usuário clicar fora da área do modal
window.onclick = function(event) {
    if (event.target == document.getElementById("myModal")) {
        closeModal();
    }
}

// Função para fechar o modal
function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}

// Requisição AJAX para buscar profissionais
function loadProfissionais(servicoId) {
    const selectProfissional = document.getElementById('modalProfissionalSelect');
    selectProfissional.innerHTML = '<option value="" disabled selected>Carregando...</option>';

    if (!servicoId) {
        selectProfissional.innerHTML = '<option value="" disabled selected>Selecione um serviço primeiro.</option>';
        return;
    }

    // 💡 ATUALIZADO: Constrói a URL substituindo o '0' pelo ID real do serviço
    const url = API_URL_BASE.replace('0', servicoId); 
    
    fetch(url) 
        .then(response => {
        // Verifica se a resposta foi bem-sucedida (status 200)
        if (!response.ok) {
            // Se a URL estiver incorreta, ele provavelmente cairá aqui
            throw new Error('Erro na requisição: ' + response.statusText + ' (' + response.status + ')');
        }
        return response.json();
    })
    .then(data => {
        selectProfissional.innerHTML = '<option value="" disabled selected>Selecione um Profissional</option>';
                    
        if (data.profissionais && data.profissionais.length > 0) {
            data.profissionais.forEach(profissional => {
                const option = document.createElement('option');
                option.value = profissional.id;
                option.textContent = profissional.nome_completo;
                selectProfissional.appendChild(option);
                });
            } else {
                selectProfissional.innerHTML = '<option value="" disabled selected>Nenhum profissional disponível.</option>';
            }
        })
        .catch(error => {
        console.error('Erro ao buscar profissionais:', error);
        selectProfissional.innerHTML = '<option value="" disabled selected>Erro ao carregar lista.</option>';
        alert("Ocorreu um erro ao carregar a lista de profissionais. Tente novamente mais tarde.");
        });
}

// Função para abrir o modal (AJUSTADA)
function openModal(servicoNome, servicoId) {
    const modal = document.getElementById('myModal');
    
    // 💡 NOVO: Define o nome do serviço visível e o ID escondido no modal
    document.getElementById('selectedServiceName').textContent = servicoNome;
    document.getElementById('modalServiceId').value = servicoId;
    
    // 2. Inicia o carregamento dos profissionais
    loadProfissionais(servicoId); 
    
    // 3. Abre o modal
    modal.style.display = 'block'; 
}

// Função para submeter o formulário (AJUSTADA)
function submitForm() {
    // 1. Captura os valores. Agora, pegamos o ID do input hidden dentro do modal.
    const servicoId = document.getElementById('modalServiceId').value;
    const dataHora = document.getElementById('datetime').value;
    const profissionalId = document.getElementById('modalProfissionalSelect').value; 

    // 2. Validação simples
    if (!servicoId || !dataHora || !profissionalId) {
        alert("Por favor, preencha todos os campos e selecione um profissional.");
        return;
    }

    // 3. Define os valores nos campos hidden de submissão do formulário principal
    document.getElementById('form_servico_id').value = servicoId;
    document.getElementById('form_data_hora').value = dataHora;
    document.getElementById('form_profissional_id').value = profissionalId; 

    // 4. Submete o formulário
    document.getElementById('agendamentoForm').submit();
}

// Adiciona um listener para o fechamento do modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('myModal');
    if (event.target == modal) {
        closeModal();
    }
}
