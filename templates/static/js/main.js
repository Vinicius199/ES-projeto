const btnLogin = document.getElementById('btnLogin');
const btnCadastro = document.getElementById('btnCadastro');

if (btnLogin) {
    btnLogin.addEventListener('click', () => {
    });
}

if (btnCadastro) {
    btnCadastro.addEventListener('click', () => {
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
    window.onclick = function(event) {
        var modal = document.getElementById('myModal');
        if (event.target == modal) {
            closeModal();
        }
    }

    const formHasErrors = document.querySelector('.errorlist, .alert-danger'); 
    if (formHasErrors) {
        const viewMode = document.getElementById('view-mode');
        if(viewMode) toggleEditMode(); 
    }
});

