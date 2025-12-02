# clientes/tests/conftest.py

import pytest
import os
import django 
from django.urls import reverse
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agenda.settings')

try:
    django.setup()
except Exception:
    pass

from clientes.models import Cliente, Servico, Agendamento


@pytest.fixture
def valid_cadastro_data():
    return {
        'nome': 'Novo',
        'sobrenome': 'User',
        'email': 'novo@user.com',
        'telefone': '11912345678', 
        'senha': 'SenhaForte123!', 
    }

@pytest.fixture
def existing_client(db):
    return Cliente.objects.create_user(
        email='existente@teste.com', 
        password='outrasenha',
        nome='Ja',
        sobrenome='Existe',
        telefone='11988887777'
    )

@pytest.fixture
def cadastro_url():
    return reverse('cadastro')

@pytest.fixture
def agendamento_url():
    return reverse('criar_agendamento')

@pytest.fixture
def login_url():
    return reverse('login')

@pytest.fixture
def home_url():
    return reverse('home')

@pytest.fixture
def servico_test(db):
    return Servico.objects.create(nome='Corte Masculino', duracao_minutos=30)

@pytest.fixture
def agendamento_valido_data(existing_client, servico_test):

    agora = datetime.now()
    hora_agendada = (agora + timedelta(hours=1)).replace(second=0, microsecond=0)
    
    return {
        'cliente': existing_client.id, 
        'servico': servico_test.id,
        'data_hora': hora_agendada.isoformat(), 
        'observacoes': 'Cortar só as pontas.'
    }

@pytest.fixture
def cria_um_cliente_profissional(db):
    # Certifique-se de que o Cliente.objects.create_user aceita 'nome', 'sobrenome', etc.
    return Cliente.objects.create_user(
        email='profissional@teste.com',
        password='SenhaForte123!',
        nome='Profissional',
        sobrenome='Teste',
        telefone='11987654321',
        # Se você tiver um campo is_profissional no modelo Cliente, defina-o aqui
        # is_profissional=True 
    )

@pytest.fixture
def cria_um_profissional_test(db, cria_um_cliente_profissional):
    from clientes.models import Profissional
    
    return Profissional.objects.create(
        user=cria_um_cliente_profissional,
    )

