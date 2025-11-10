document.addEventListener('DOMContentLoaded', function() {

    const funcionarioModal = document.getElementById('funcionarioModal');
    const servicoModal = document.getElementById('servicoModal');
    const viewFuncionarioModal = document.getElementById('viewFuncionarioModal');
    const viewServicoModal = document.getElementById('viewServicoModal');

    // Botões de abertura
    const openFuncBtn = document.getElementById('openFuncionarioModal');
    const openServBtn = document.getElementById('openServicoModal');
    const openViewFuncionarioBtn = document.getElementById('openViewFuncionarioModal');
    const openViewServicoBtn = document.getElementById('openViewServicoModal');
    
    // Botões de fechar (X)
    const closeBtns = document.querySelectorAll('.close-btn');

    // URL base para redirecionamento (limpa os parâmetros de edição)
    const adminPainelUrl = new URL(window.location.href);
    adminPainelUrl.pathname = adminPainelUrl.pathname.replace(/funcionario\/editar\/\d+\/|servico\/editar\/\d+\//, '');


    // --- FUNÇÕES AUXILIARES ---

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
            // Se fechar no modo de edição, redireciona para limpar o estado
            if (document.body.classList.contains('editing-mode')) {
                // Remove a classe do corpo para garantir que não tente reabrir ao voltar
                document.body.classList.remove('editing-mode');
                window.location.href = adminPainelUrl.toString();
            }
        }
    }
    
    // Função genérica para exibir mensagens no topo do container
    function showMessage(message, type, targetElement) {
        // Remove mensagens anteriores do mesmo tipo/target
        targetElement.querySelectorAll('.alert').forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`; 
        
        // Formata a mensagem para quebrar linhas se houver detalhes de erro
        alertDiv.innerHTML = message.replace(/\n/g, '<br>');

        targetElement.prepend(alertDiv); 

        // Remove a mensagem após 5 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    // Abrir Modais de Cadastro/Visualização
    if (openFuncBtn) openFuncBtn.addEventListener('click', () => openModal(funcionarioModal));
    if (openServBtn) openServBtn.addEventListener('click', () => openModal(servicoModal));

    // Abrir Modais de Visualização
    if (openViewFuncionarioBtn) openViewFuncionarioBtn.addEventListener('click', () => openModal(viewFuncionarioModal));
    if (openViewServicoBtn) openViewServicoBtn.addEventListener('click', () => openModal(viewServicoModal));


    // Fechar usando o botão (X)
    closeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal-target');
            closeModal(modalId);
        });
    });

    // Fechar ao clicar fora do modal
    window.addEventListener('click', function(event) {
        document.querySelectorAll('.modal').forEach(modal => {
            if (event.target === modal) {
                closeModal(modal.id); // Reusa a função closeModal para tratar o redirecionamento de edição
            }
        });
    });

    // Forçar abertura do modal se estiver no modo de edição (Renderizado pelo Django)
    if (document.body.classList.contains('editing-mode')) {
        const funcModal = document.getElementById('funcionarioModal');
        const servModal = document.getElementById('servicoModal');
        
        // Verifica se a classe 'modal-open' foi adicionada pelo HTML
        if (funcModal && funcModal.classList.contains('modal-open')) {
            openModal(funcModal);
        }
        if (servModal && servModal.classList.contains('modal-open')) {
            openModal(servModal);
        }
    }


    
    // Função genérica para submissão AJAX usando Fetch
    async function handleFormSubmit(event, modalElement) {
        event.preventDefault(); 
        
        const form = event.target;
        const submitBtn = form.querySelector('.btn-submit');
        
        // Otimização: Guarda o texto original do botão
        const originalBtnText = submitBtn.textContent; 
        
        const isEditing = form.action.includes('/editar/'); 

        if (isEditing) {
            // Se for edição, usamos o submit padrão do Django para lidar com formset e redirects
            // Note que se o form de edição não usa AJAX, ele fará um POST tradicional
            form.submit();
            return; 
        }
        
        // AJAX (apenas para CADASTRO)
        const formData = new FormData(form);
        const csrftoken = getCookie('csrftoken'); // Obtém o token do cookie

        submitBtn.disabled = true;
        submitBtn.textContent = 'Salvando...';

        // Limpa mensagens anteriores de erro no formulário
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

            // Tenta ler a resposta como JSON
            const result = await response.json();

            if (response.ok && (response.status === 201 || response.status === 200)) {
                
                showMessage(result.mensagem, 'success', document.querySelector('.container')); 
                form.reset();
                
                // Redireciona após 1 segundo para limpar o formulário e recarregar dados (se houver)
                setTimeout(() => {
                    window.location.href = adminPainelUrl.toString();
                }, 1000); 

            } else {
                // Trata erros de validação (400) ou erros internos (500)
                let errorMessage = result.mensagem || 'Ocorreu um erro desconhecido.';
                
                if (result.erros) {
                    // Monta a lista de erros de validação (ex: campo: erro1, erro2)
                    let errorList = Object.entries(result.erros).map(([field, errors]) => 
                        `${field}: ${errors.join(', ')}`
                    ).join('\n');
                    
                    // Adiciona quebras de linha à mensagem principal
                    errorMessage += '\nDetalhes: ' + errorList;
                }
                
                // Exibe a mensagem de erro no modal
                showMessage(errorMessage, 'error', modalElement.querySelector('.modal-content') || form);
            }
        } catch (error) {
            console.error('Erro na submissão:', error);
            // Exibe erro de conexão no modal
            showMessage('Erro de conexão com o servidor. Verifique o console para detalhes.', 'error', modalElement.querySelector('.modal-content') || form);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalBtnText; 
        }
    }

    // Aplica a submissão aos formulários de Cadastro
    const formFuncionario = document.getElementById('formFuncionario');
    if (formFuncionario) formFuncionario.addEventListener('submit', (e) => handleFormSubmit(e, funcionarioModal));

    const formServico = document.getElementById('formServico');
    if (formServico) formServico.addEventListener('submit', (e) => handleFormSubmit(e, servicoModal));

});