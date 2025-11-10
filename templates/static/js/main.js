// Referências aos botões
const btnLogin = document.getElementById('btnLogin');
const btnCadastro = document.getElementById('btnCadastro');

// Eventos de clique (simples) 
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

// Função para obter o CSRF Token 
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

function closeModal() {
    document.getElementById('myModal').style.display = 'none';
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

