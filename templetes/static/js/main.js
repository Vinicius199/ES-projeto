// Referências aos botões
const btnLogin = document.getElementById('btnLogin');
const btnCadastro = document.getElementById('btnCadastro');

// Eventos de clique (simples)
btnLogin.addEventListener('click', () => {
  //alert('Redirecionar para tela de login');
});

btnCadastro.addEventListener('click', () => {
  //alert('Redirecionar para tela de cadastro');
});

// ====== LÓGICA DE CADASTRO ======
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("cadastroForm");

  form.addEventListener("submit", (e) => {
    e.preventDefault();  // Impede o envio do formulário padrão

    const formData = new FormData(form);  // Cria um FormData a partir do formulário

    // Validação do telefone no frontend
    const telefone = formData.get('telefone');
    const telefoneLimpo = telefone.replace(/\D/g, '');  // Remove caracteres não numéricos

    // Verifica se o telefone tem 10 ou 11 dígitos
    if (telefoneLimpo.length < 10 || telefoneLimpo.length > 11) {
      alert("O número de telefone deve ter 10 ou 11 dígitos.");
      return;
    }

    // Verifica se o telefone contém apenas números
    if (!/^\d+$/.test(telefoneLimpo)) {
      alert("O número de telefone deve conter apenas números.");
      return;
    }

    // Verifica se o DDD é válido (dois primeiros dígitos devem ser entre 11 e 99)
    const ddd = telefoneLimpo.slice(0, 2);
    if (!/^[1-9][0-9]$/.test(ddd)) {
      alert("O DDD deve ser válido (exemplo: 11 para São Paulo).");
      return;
    }

    // Envio para API Django
    fetch("/cadastro/", {
      method: "POST",
      body: formData  // Envia os dados do formulário como FormData
    })
    .then(res => res.json())
    .then(data => {
      if (data.message) {
        form.reset();  // Limpa todos os campos do formulário
        if (data.redirect_url) {
          window.location.href = data.redirect_url;  // Redireciona para a URL recebida
        }
      } else if (data.errors) {
        document.getElementById("error-messages").innerHTML = '';
        Object.keys(data.errors).forEach(field => {
          const errorMessages = data.errors[field];
          const fieldElement = document.getElementById(field);
          if (fieldElement) {
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('error-message');
            errorDiv.textContent = errorMessages.join(", ");
            fieldElement.parentElement.appendChild(errorDiv);
          }
        });
      } else {
        alert(`Erro desconhecido: ${data.error}`);
      }
    })
    .catch(err => {
      console.error("Erro:", err);
      alert("Email já cadastrado.");
    });
  });
});

// ====== FIM DA LÓGICA DE CADASTRO ======

// ====== LÓGICA DE LOGIN ======

$(document).ready(function() {
    $("#loginForm").on('submit', function(event) {
       event.preventDefault();  // Impede o envio normal do formulário

        // Limpa as mensagens de erro e sucesso
        $("#errorMessages").html('');
         $("#successMessage").html('');

          $.ajax({
            url: '{% url "login" %}',  // URL para o login
            method: 'POST',
            data: {
              'email': $('#email').val(),
              'senha': $('#senha').val(),
              'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    $("#successMessage").html(response.message);
                    window.location.href = "{% url 'home' %}";  // Redireciona para a home após sucesso
                } else {
                    $("#errorMessages").html(response.message);  // Exibe erro genérico
                    if (response.errors) {
                        // Exibe erros específicos de cada campo
                        $.each(response.errors, function(field, messages) {
                            $.each(messages, function(_, message) {
                                $("#errorMessages").append('<p>' + message.message + '</p>');
                            });
                        });
                    }
                }
            },
              error: function(xhr, status, error) {
                  $("#errorMessages").html('Ocorreu um erro. Tente novamente.');
              }
          });
      });
});

