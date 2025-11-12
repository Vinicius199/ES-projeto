function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
         if (modalId === 'modalProfissionais') {
            populateProfessionalList();
            showProfessionalSelection(); // Garante que a primeira etapa é exibida
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// ===================================
// Lógica de Seleção de Profissional (Modal 2)
// ===================================

function showProfessionalSelection() {
    const selection = document.getElementById('professionalSelection');
    const display = document.getElementById('scheduleDisplay');
    const title = document.getElementById('modalProfissionaisTitle');

    if (selection && display && title) {
        selection.style.display = 'block';
        display.style.display = 'none';
        title.textContent = 'Agendamentos dos Profissionais';
    }
}

function populateProfessionalList() {
    const list = document.getElementById('professionalList');
    if (!list) return; // Garante que o elemento existe

    list.innerHTML = ''; // Limpa a lista anterior
    professionals.forEach(prof => {
        const item = document.createElement('div');
        item.className = 'professional-item';
        item.setAttribute('data-id', prof.id);
        item.innerHTML = `<strong>${prof.name}</strong><br><small>Especialidade: ${prof.specialization}</small>`;

        // Usando addEventListener para melhor prática
        item.addEventListener('click', () => selectProfessional(prof.id, prof.name));
        list.appendChild(item);
    });
}

function selectProfessional(id, name) {
    const professionalSelection = document.getElementById('professionalSelection');
    const selectedProfName = document.getElementById('selectedProfName');
    const modalProfissionaisTitle = document.getElementById('modalProfissionaisTitle');
    const scheduleDisplay = document.getElementById('scheduleDisplay');

    if (professionalSelection && selectedProfName && modalProfissionaisTitle && scheduleDisplay) {
        // Oculta a lista de profissionais
        professionalSelection.style.display = 'none';

        // Atualiza o título e exibe a área de horários
        selectedProfName.textContent = `Horários de: ${name}`;
        modalProfissionaisTitle.textContent = `Agenda de ${name}`;
        scheduleDisplay.style.display = 'block';

        displaySchedules(id);
    }
}

function displaySchedules(profId) {
    const scheduleDiv = document.getElementById('availableSchedules');
    if (!scheduleDiv) return;

    scheduleDiv.innerHTML = ''; // Limpa os horários anteriores
    const profSchedules = schedules[profId] || [];

    if (profSchedules.length === 0) {
        scheduleDiv.innerHTML = '<p style="color: red;">Nenhum horário agendado ou disponível.</p>';
        return;
    }

    profSchedules.forEach(schedule => {
        const date = new Date(schedule.datetime);
        // Formato: DD/MM/AAAA e HH:MM
        const dateString = date.toLocaleDateString('pt-BR');
        const timeString = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

        const item = document.createElement('div');
        item.className = 'schedule-item';
        item.setAttribute('data-datetime', schedule.datetime);
        item.innerHTML = `<strong>${dateString}</strong><br>${timeString}`;

        scheduleDiv.appendChild(item);
    });
}

document.addEventListener('DOMContentLoaded', function() {

    // 1. Adiciona event listeners aos botões de abrir
    const btnMeusAgendamentos = document.getElementById('btnMeusAgendamentos');
    const btnProfissionais = document.getElementById('btnProfissionais');
    const backToProfessionals = document.getElementById('backToProfessionals');

    if (btnMeusAgendamentos) {
        btnMeusAgendamentos.addEventListener('click', function() {
            openModal('modalMeusAgendamentos');
        });
    }

    if (btnProfissionais) {
        btnProfissionais.addEventListener('click', function() {
            openModal('modalProfissionais');
        });
    }

// 2. Adiciona event listeners aos botões de fechar (x)
    document.querySelectorAll('.close-btn').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            closeModal(modalId);
        });
    });

    // 3. Adiciona evento para o link "Voltar"
    if (backToProfessionals) {
        backToProfessionals.addEventListener('click', function(e) {
            e.preventDefault();
            showProfessionalSelection();
        });
    }

    // 4. Fechar Modais ao Clicar Fora (área externa)
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    });

});

// Adiciona o token CSRF globalmente para chamadas AJAX
const csrfToken = "{{ csrf_token }}";