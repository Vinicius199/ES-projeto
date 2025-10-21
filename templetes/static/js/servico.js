// Função para abrir o modal
function openModal(serviceName) {
    document.getElementById("serviceName").textContent = serviceName;
    document.getElementById("myModal").style.display = "block";
}

// Função para fechar o modal
function closeModal() {
    document.getElementById("myModal").style.display = "none";
}

// Função para submeter o agendamento
function submitForm() {
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const datetime = document.getElementById("datetime").value;

    if (name && email && datetime) {
        alert("Agendamento confirmado para " + name + " em " + datetime);
        closeModal();
    } else {
        alert("Por favor, preencha todos os campos!");
    }
}

// Fechar o modal se o usuário clicar fora da área do modal
window.onclick = function(event) {
    if (event.target == document.getElementById("myModal")) {
        closeModal();
    }
}