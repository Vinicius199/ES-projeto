function showMessage(message, type, targetElement) {
    const displayTime = 5000; 
    
    targetElement.querySelectorAll('.alert').forEach(alert => alert.remove());

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`; 
    alertDiv.innerHTML = message.replace(/\n/g, '<br>');

    targetElement.prepend(alertDiv); 
    
    alertDiv.addEventListener('transitionend', function() {
        if (alertDiv.classList.contains('fade-out')) {
            alertDiv.remove();
        }
    });

    setTimeout(() => {
        if (alertDiv) {
            alertDiv.classList.add('fade-out');
        }
    }, displayTime);
    
}

function handleDjangoMessages() {
    const alerts = document.querySelectorAll('.alert'); 
    const displayTime = 5000; 

    alerts.forEach(alert => {
        alert.addEventListener('transitionend', function() {
            if (alert.classList.contains('fade-out')) {
                alert.remove();
            }
        });
        
        setTimeout(() => {
            alert.classList.add('fade-out');
        }, displayTime);
    });
}

document.addEventListener('DOMContentLoaded', function() {

    const funcionarioModal = document.getElementById('funcionarioModal');
    const servicoModal = document.getElementById('servicoModal');
    const viewFuncionarioModal = document.getElementById('viewFuncionarioModal');
    const viewServicoModal = document.getElementById('viewServicoModal');

    const openFuncBtn = document.getElementById('openFuncionarioModal');
    const openServBtn = document.getElementById('openServicoModal');
    const openViewFuncionarioBtn = document.getElementById('openViewFuncionarioModal');
    const openViewServicoBtn = document.getElementById('openViewServicoModal');
    
    const closeBtns = document.querySelectorAll('.close-btn');

    const adminPainelUrl = new URL(window.location.href);
    adminPainelUrl.pathname = adminPainelUrl.pathname.replace(/funcionario\/editar\/\d+\/|servico\/editar\/\d+\//, '');

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

    function openModal(modal) {
        if (modal) {
            modal.style.display = "block";
        }
    }

    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = "none";
            if (document.body.classList.contains('editing-mode')) {
                document.body.classList.remove('editing-mode');
                window.location.href = adminPainelUrl.toString();
            }
        }
    }
    function updateServicoSelect(profissionais) {
        const selectServico = document.getElementById('funcionarios_servico');
        if (!selectServico) return;
        
        selectServico.innerHTML = ''; // Limpa as opções antigas
        
        if (profissionais && profissionais.length > 0) {
            profissionais.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = `${p.nome} ${p.sobrenome}`; 
                selectServico.appendChild(option);
            });
        } else {
             const option = document.createElement('option');
             option.value = "";
             option.disabled = true;
             option.textContent = "Nenhum profissional cadastrado.";
             selectServico.appendChild(option);
        }
    }

    function updateViewFuncionarioTable(profissionais) {
        const tableBody = document.querySelector('#viewFuncionarioModal .list-table tbody');
        if (!tableBody) return;
        
        tableBody.innerHTML = ''; 
        const csrftoken = getCookie('csrftoken');
        
        if (profissionais && profissionais.length > 0) {
            profissionais.forEach(p => {
                const row = tableBody.insertRow();
                
                row.insertCell().textContent = p.id;
                row.insertCell().textContent = `${p.nome} ${p.sobrenome}`;
                row.insertCell().textContent = p.email || "N/A"; 
                
                const actionsCell = row.insertCell();
                
                const editUrl = `/admin-painel/funcionario/editar/${p.id}/`;
                actionsCell.innerHTML += `<a href="${editUrl}" class="action-link btn-edit">✏️ Editar</a>`;
                
                const deleteUrl = `/admin-painel/funcionario/excluir/${p.id}/`;
                actionsCell.innerHTML += `
                    <form action="${deleteUrl}" method="POST" style="display:inline;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                        <button type="submit" class="action-link btn-delete" onclick="return confirm('Tem certeza que deseja excluir este funcionário?');">❌ Excluir</button>
                    </form>
                `;
            });
        } else {
            const row = tableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 4;
            cell.textContent = "Nenhum funcionário cadastrado.";
        }
    }

    handleDjangoMessages();


    if (openFuncBtn) openFuncBtn.addEventListener('click', () => openModal(funcionarioModal));
    if (openServBtn) openServBtn.addEventListener('click', () => openModal(servicoModal));

    if (openViewFuncionarioBtn) openViewFuncionarioBtn.addEventListener('click', () => openModal(viewFuncionarioModal));
    if (openViewServicoBtn) openViewServicoBtn.addEventListener('click', () => openModal(viewServicoModal));


    // Fechar usando o botão (X)
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-target');
            closeModal(modalId);
        });
    });

    window.addEventListener('click', function(event) {
        document.querySelectorAll('.modal').forEach(modal => {
            if (event.target === modal) {
                closeModal(modal.id); 
            }
        });
    });

    if (document.body.classList.contains('editing-mode')) {
        const funcModal = document.getElementById('funcionarioModal');
        const servModal = document.getElementById('servicoModal');

        if (funcModal && funcModal.classList.contains('modal-open')) {
            openModal(funcModal);
        }
        if (servModal && servModal.classList.contains('modal-open')) {
            openModal(servModal);
        }
    }

    async function handleFormSubmit(event, modalElement) {
        event.preventDefault(); 
 
        const form = event.target;
        const submitBtn = form.querySelector('.btn-submit');
        const formId = form.id; 
 
        const originalBtnText = submitBtn.textContent; 
 
        const isEditing = form.action.includes('/editar/'); 

        if (isEditing) {
            form.submit();
            return; 
        }

        const formData = new FormData(form);
        const csrftoken = getCookie('csrftoken'); 

        submitBtn.disabled = true;
        submitBtn.textContent = 'Salvando...';

        form.querySelectorAll('.alert').forEach(alert => alert.remove());

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (response.ok && (response.status === 201 || response.status === 200)) {

                showMessage(result.mensagem, 'success', document.querySelector('.container')); 
                form.reset();

                if (formId === 'formFuncionario' && result.profissionais_list) {

                    updateServicoSelect(result.profissionais_list);

                    updateViewFuncionarioTable(result.profissionais_list); 

                    closeModal(modalElement.id); 

                } else {
                    setTimeout(() => {
                        window.location.href = adminPainelUrl.toString();
                    }, 1000); 
                }

            } else {

                let errorMessage = result.mensagem || 'Ocorreu um erro desconhecido.';

                if (result.erros) {
                    let errorList = Object.entries(result.erros).map(([field, errors]) => {
        
                        // Correção para garantir que .join() só seja chamado em arrays
                        const errorMessages = Array.isArray(errors) ? errors.join(', ') : errors;
                        return `${field}: ${errorMessages}`;
                    
                    }).join('\n');

                    errorMessage += '\nDetalhes: ' + errorList;
                }

                showMessage(errorMessage, 'error', modalElement.querySelector('.modal-content') || form);
            }
        } catch (error) {
            console.error('Erro na submissão:', error);
            showMessage('Erro de conexão com o servidor. Verifique o console para detalhes.', 'error', modalElement.querySelector('.modal-content') || form);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText; 
        }
    }

    const formFuncionario = document.getElementById('formFuncionario');
    if (formFuncionario) formFuncionario.addEventListener('submit', (e) => handleFormSubmit(e, funcionarioModal));

    const formServico = document.getElementById('formServico');
    if (formServico) formServico.addEventListener('submit', (e) => handleFormSubmit(e, servicoModal));

});