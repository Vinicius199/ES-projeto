import pytest
from django.urls import reverse
from django.contrib.messages import get_messages
from clientes.models import Cliente 

@pytest.mark.django_db
def test_carregamento_com_sucesso_da_pagina_cadastro(client, cadastro_url):
    #Verifica se a view retorna status 200 e usa o template correto no GET
    
    response = client.get(cadastro_url)
    
    assert response.status_code == 200
    assert 'cadastro.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_cadastro_bem_sucedido_e_redirecionamento(client, cadastro_url, login_url, valid_cadastro_data):
    
    response = client.post(cadastro_url, valid_cadastro_data, follow=True)
    
    assert Cliente.objects.filter(email=valid_cadastro_data['email']).exists()
    assert response.redirect_chain[-1][0] == login_url 
    assert response.status_code == 200
    
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'

@pytest.mark.django_db
def test_cadasto_por_dados_invalidos(client, cadastro_url, valid_cadastro_data):
    
    invalid_data = valid_cadastro_data.copy()
    invalid_data['telefone'] = '119876543' # 7 digitos telefone inválido fora o DDD
    
    response = client.post(cadastro_url, invalid_data, follow=True)
    
    assert Cliente.objects.count() == 0
    assert response.status_code == 200 
    
    messages = list(get_messages(response.wsgi_request))
    assert messages[0].level_tag == 'error'

@pytest.mark.django_db
def test_login_bem_sucedido_e_redireciona(client, login_url, home_url, existing_client):
    #Verifica se um login bem-sucedido autentica o usuário e redireciona para home.
    
    login_data = {
        'email': existing_client.email,
        'senha': 'outrasenha',
    }
    
    response = client.post(login_url, login_data, follow=True)
    
    assert response.context['user'].is_authenticated
    assert response.redirect_chain[-1][0] == home_url

@pytest.mark.django_db
def test_falha_no_login(client, login_url, existing_client):
    #Verifica se são inválidas as credenciais e falha no login e mostram mensagem de erro
    
    login_data = {
        'email': existing_client.email,
        'senha': 'SenhaErrada999',
    }
    
    response = client.post(login_url, login_data, follow=True)
    
    assert not response.context['user'].is_authenticated
    assert response.status_code == 200
    
    messages = list(get_messages(response.wsgi_request))
    assert messages[0].level_tag == 'error'
    assert "E-mail ou senha inválidos." in str(messages[0])