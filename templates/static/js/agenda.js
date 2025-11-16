let professionals = []; 
let schedules = {}; 
const API_URL = '/api/agendamentos-profissionais/';

function hideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    const displayTime = 5000; 
    const fadeOutTime = 500; 

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade-out');
            
            setTimeout(() => {
                alert.remove();
            }, fadeOutTime); 

        }, displayTime);
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        if (modalId === 'modalProfissionais') {
            fetchSchedulesAndProfessionals(); 
            showProfessionalSelection();
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

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

function fetchSchedulesAndProfessionals() {
    const list = document.getElementById('professionalList');
    if (!list) 
        return;

    if (professionals.length > 0) {
        populateProfessionalList();
        return;
    }
    
    list.innerHTML = '<p style="text-align: center; color: #007bff;">Carregando profissionais e agendas...</p>';

    fetch(API_URL)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro ${response.status}: Falha na comunicação com o servidor.`);
            }
            return response.json();
        })
        .then(data => {
            professionals = data.professionals; 
            schedules = data.schedules; 
            populateProfessionalList();
        })
        .catch(error => {
            console.error('Erro de Fetch:', error);
            // Exibe o erro na área da lista de profissionais
            list.innerHTML = `<p class="alert alert-error" style="text-align: center;">Não foi possível carregar a lista de profissionais. Detalhes: ${error.message}</p>`;
        });
}

function populateProfessionalList() {
    const list = document.getElementById('professionalList');
    if (!list) return;

    list.innerHTML = ''; 
    
    if (professionals.length === 0) {
        list.innerHTML = '<p>Nenhum profissional cadastrado.</p>';
        return;
    }

    professionals.forEach(prof => {
        const item = document.createElement('div');
        item.className = 'professional-item';
        item.setAttribute('data-id', prof.id);
        
        item.innerHTML = `<strong>${prof.name}</strong>`; 

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
        professionalSelection.style.display = 'none';
        selectedProfName.textContent = `Horários de: ${name}`;
        modalProfissionaisTitle.textContent = `Agenda de ${name}`;
        scheduleDisplay.style.display = 'block';

        displaySchedules(id);
    }
}

function displaySchedules(profId) {
    const scheduleDiv = document.getElementById('availableSchedules');
    if (!scheduleDiv) return;

    scheduleDiv.innerHTML = ''; 
    const profSchedules = schedules[profId] || []; 

    if (profSchedules.length === 0) {
        scheduleDiv.innerHTML = '<p class="alert alert-warning" style="text-align: center;">Nenhum agendamento futuro encontrado para este profissional.</p>';
        return;
    }
    
    let tableHTML = `
        <table class="list-table">
            <thead>
                <tr>
                    <th>Data e Hora</th>
                    <th>Serviço</th>
                    <th>Cliente</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    `;

    profSchedules.forEach(schedule => {
        const date = new Date(schedule.datetime);
        const dateString = date.toLocaleDateString('pt-BR');
        const timeString = date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        
        const statusClass = schedule.status === 'Confirmado' ? 'bg-success' : 'bg-warning';
        
        tableHTML += `
            <tr>
                <td>${dateString} ${timeString}</td>
                <td>${schedule.service_name}</td>
                <td>${schedule.client_name}</td>
                <td><span class="badge ${statusClass}">${schedule.status}</span></td>
            </tr>
        `;
    });
    
    tableHTML += '</tbody></table>';
    
    scheduleDiv.innerHTML = tableHTML;
}

document.addEventListener('DOMContentLoaded', function() {
    
    hideAlerts();
   
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

    document.querySelectorAll('.close-btn').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            closeModal(modalId);
        });
    });

    if (backToProfessionals) {
        backToProfessionals.addEventListener('click', function(e) {
            e.preventDefault();
            showProfessionalSelection();
        });
    }

    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    });
});