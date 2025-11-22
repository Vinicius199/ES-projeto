import pytest
from clientes.forms import CadastroForm, LoginForm
from clientes.models import Cliente 

@pytest.mark.django_db
def test_email_duplicado(existing_client, valid_cadastro_data):
    
    # Prepara dados duplicados
    duplicate_data = valid_cadastro_data.copy()
    duplicate_data['email'] = existing_client.email
    
    form = CadastroForm(data=duplicate_data)
    
    assert not form.is_valid()
    assert 'email' in form.errors
    assert "Este e-mail já está cadastrado." in form.errors['email'][0]

@pytest.mark.django_db
def test_telefone_invalido(valid_cadastro_data):
    #Verifica se o form levanta erro para telefones com menos de 10 dígitos.
    
    invalid_data = valid_cadastro_data.copy()
    invalid_data['telefone'] = '119876543' 
    
    form = CadastroForm(data=invalid_data)
    
    assert not form.is_valid()
    assert 'telefone' in form.errors
    assert "O número de telefone deve ter 10 ou 11 dígitos, incluindo o DDD." in form.errors['telefone'][0]

@pytest.mark.django_db
def test_salvamento_com_hashing_da_senha(valid_cadastro_data):
    
    form = CadastroForm(data=valid_cadastro_data)
    assert form.is_valid()
    
    user = form.save()
    
    # Verifica se o usuário foi criado no BD
    assert Cliente.objects.filter(email=valid_cadastro_data['email']).exists()
    # Verifica se a senha foi hasheada
    assert user.check_password(valid_cadastro_data['senha'])

@pytest.mark.django_db
def test_login_bem_sucedido(existing_client):
    
    valid_data = {
        'email': existing_client.email,
        'senha': 'outrasenha', 
    }
    form = LoginForm(data=valid_data)
    
    assert form.is_valid()

@pytest.mark.django_db
def test_erro_senha_incorreta(existing_client):
    
    invalid_data = {
        'email': existing_client.email,
        'senha': 'SenhaErrada123',
    }
    form = LoginForm(data=invalid_data)
    
    assert not form.is_valid()
    # Erro é retornado para erros de autenticação
    assert 'Email ou senha incorretos.' in form.errors['__all__'][0]