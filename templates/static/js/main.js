// Referências aos botões (MANTIDAS)
const btnLogin = document.getElementById('btnLogin');
const btnCadastro = document.getElementById('btnCadastro');

// Eventos de clique (simples) (MANTIDOS)
if (btnLogin) {
    btnLogin.addEventListener('click', () => {
        // Lógica de redirecionamento ou ação de login
    });
}

if (btnCadastro) {
    btnCadastro.addEventListener('click', () => {
        // Lógica de redirecionamento ou ação de cadastro
    });
}

// Função para obter o CSRF Token (MANTIDA, mas não usada diretamente neste contexto de POST via form)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
 
// 💡 FUNÇÃO ATUALIZADA: Agora pré-seleciona o serviço no DROPDOWN
function openModal(serviceName, serviceId) {
    const modal = document.getElementById('myModal');
    const serviceSelect = document.getElementById('modalServiceSelect');
    const dateTimeInput = document.getElementById('datetime');

    // 1. Pré-seleciona o serviço clicado no novo campo <select>
    if (serviceSelect && serviceId) {
        serviceSelect.value = serviceId; 
    }

    // 2. Configura a data mínima para evitar agendamento no passado (melhora a UX)
    const now = new Date();
    // Ajusta para ter um tempo mínimo correto (evita problemas de fuso horário no `datetime-local`)
    const offset = now.getTimezoneOffset() * 60000;
    const localISOTime = (new Date(Date.now() - offset)).toISOString().slice(0, 16);
    
    dateTimeInput.min = localISOTime;

    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}

// 💡 FUNÇÃO ATUALIZADA: Agora obtém o ID do serviço do DROPDOWN
function submitForm() {
    // Referência ao novo campo <select>
    const serviceSelect = document.getElementById('modalServiceSelect');
    const dataHora = document.getElementById('datetime').value;
    
    // Obtém o ID do serviço selecionado no dropdown
    const servicoId = serviceSelect.value;
            
    if (!dataHora || !servicoId) {
        alert("Por favor, selecione um serviço e uma data/hora.");
        return;
    }
            
    // Preenche os campos ocultos do formulário POST com os valores do modal
    document.getElementById('form_servico_id').value = servicoId;
    document.getElementById('form_data_hora').value = dataHora;
            
    // Envia o formulário para a view
    document.getElementById('agendamentoForm').submit();
}

// Funções de toggle/erro (MANTIDAS, embora pareçam ser para outra parte da aplicação)
function toggleEditMode() {
    const viewMode = document.getElementById('view-mode');
    const editMode = document.getElementById('edit-mode');

    if (viewMode.style.display === 'block') {
        viewMode.style.display = 'none';
        editMode.style.display = 'block';
    } else {
        viewMode.style.display = 'block';
        editMode.style.display = 'none';
    }
}
    
document.addEventListener('DOMContentLoaded', function() {
    // Fecha o modal ao clicar fora dele
    window.onclick = function(event) {
        var modal = document.getElementById('myModal');
        if (event.target == modal) {
            closeModal();
        }
    }

    // Se houver erros de formulário no POST, garantimos que o modo de edição permaneça visível (MANTIDO)
    const formHasErrors = document.querySelector('.errorlist, .alert-danger'); 
    if (formHasErrors) {
        const viewMode = document.getElementById('view-mode');
        if(viewMode) toggleEditMode(); 
    }
});