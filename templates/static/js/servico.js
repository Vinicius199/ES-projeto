function closeServiceModal() {
    const modal = document.getElementById('myModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('myModal');
    if (event.target == modal) {
            closeServiceModal();
    }
}

function loadProfissionais(servicoId) {
    const selectProfissional = document.getElementById('modalProfissionalSelect');
    
    const agendamentoForm = document.getElementById('agendamentoForm');
    const apiUrlBase = agendamentoForm ? agendamentoForm.dataset.apiUrl : null; 

    if (!selectProfissional) {
        console.error("Erro: Elemento 'modalProfissionalSelect' não encontrado.");
        return; 
    }
    
    selectProfissional.innerHTML = '<option value="" disabled selected>Carregando...</option>';

    if (!servicoId) {
        selectProfissional.innerHTML = '<option value="" disabled selected>Selecione um serviço primeiro.</option>';
        return;
    }
    
    // Testa se a URL foi encontrada no DOM
    if (!apiUrlBase) {
        console.error("Erro fatal: A URL base da API (data-api-url) não foi encontrada no formulário.");
        selectProfissional.innerHTML = '<option value="" disabled selected>Erro de configuração (URL não injetada).</option>';
        return;
    }

    const url = apiUrlBase.replace('0', servicoId); 
    
    fetch(url) 
        .then(response => {
        if (!response.ok) {
            throw new Error('Erro na requisição AJAX: ' + response.statusText + ' (' + response.status + ')');
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
        // Se cair aqui, a requisição falhou, mas a URL estava definida.
        console.error('Falha ao buscar profissionais (Verifique a aba Network):', error);
        selectProfissional.innerHTML = '<option value="" disabled selected>Erro ao carregar lista.</option>';
        alert("Ocorreu um erro ao carregar a lista de profissionais. Verifique a aba Network (F12) para detalhes.");
        });
}

function openServiceModal(serviceName, serviceId) {
    const modal = document.getElementById('myModal');
    const serviceNameSpan = document.getElementById('selectedServiceName'); 
    const serviceIdInput = document.getElementById('modalServiceId'); 
    const dateTimeInput = document.getElementById('datetime');

    if (!modal) {
        console.error("Erro: Elemento 'myModal' não encontrado.");
        return; 
    }

    if (serviceNameSpan && serviceIdInput && serviceId) {
        serviceNameSpan.textContent = serviceName;
        serviceIdInput.value = serviceId;
    }

    loadProfissionais(serviceId);

    // Configura a data mínima
    const now = new Date();
    const offset = now.getTimezoneOffset() * 60000;
    const localISOTime = (new Date(Date.now() - offset)).toISOString().slice(0, 16);
    
    if (dateTimeInput) {
        dateTimeInput.min = localISOTime;
    }

    modal.style.display = 'block'; 
}

function submitForm() {
    const servicoId = document.getElementById('modalServiceId').value;
    const dataHora = document.getElementById('datetime').value;
    const profissionalSelect = document.getElementById('modalProfissionalSelect');
    const profissionalId = profissionalSelect ? profissionalSelect.value : null; 
    const form = document.getElementById('agendamentoForm');

    let isValid = true;
    let errorMessage = "";

    if (!servicoId) {
        isValid = false;
        errorMessage = "Erro interno: O ID do serviço não foi capturado.";
    }
    
    if (!dataHora) {
        isValid = false;
        errorMessage = "Por favor, selecione a Data e Hora.";
    } 
    
    if (!profissionalId || profissionalSelect.selectedIndex <= 0) {
        isValid = false;
        errorMessage = "Por favor, selecione um Profissional.";
    }

    if (!isValid) {
        alert(errorMessage);
        return; 
    }

    const formServicoId = document.getElementById('form_servico_id');
    const formDataHora = document.getElementById('form_data_hora');
    const formProfissionalId = document.getElementById('form_profissional_id');

    if (formServicoId && formDataHora && formProfissionalId) {
        formServicoId.value = servicoId;
        formDataHora.value = dataHora;
        formProfissionalId.value = profissionalId; 
    } else {
        console.error("Erro fatal: Campos hidden do formulário principal não encontrados.");
        alert("Erro ao preparar o formulário. Tente novamente.");
        return;
    }

    if (form) {
        console.log("Submetendo formulário...");
        form.submit();
    } else {
        console.error("Erro fatal: Formulário 'agendamentoForm' não encontrado.");
    }
}