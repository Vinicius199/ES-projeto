import pytest
from clientes.models import Agendamento
from datetime import datetime, timedelta
from django.utils import timezone

@pytest.fixture
def agendamento_existente(existing_client, servico_test, cria_um_profissional_test):

    inicio_naive = (datetime.now() + timedelta(minutes=5)).replace(second=0, microsecond=0)
    
    inicio_aware = timezone.make_aware(inicio_naive)
     
    return Agendamento.objects.create(
        cliente=existing_client,
        servico=servico_test,
        # Usa o objeto aware
        data_hora=inicio_aware, 
        Profissional=cria_um_profissional_test,

    )

@pytest.mark.django_db
def test_cria_agendamento_com_sucesso(client, agendamento_url, agendamento_valido_data, existing_client, cria_um_profissional_test):
    
    client.force_login(existing_client)
    assert Agendamento.objects.count() == 0
    
    agendamento_valido_data['Profissional'] = cria_um_profissional_test.pk
    
    if 'cliente' in agendamento_valido_data:
        del agendamento_valido_data['cliente'] 
        

    response = client.post(agendamento_url, agendamento_valido_data, follow=True)
    if Agendamento.objects.count() == 0:
        print("\n erro conteudo resposta:")
        print(response.content)    
    
    assert Agendamento.objects.count() == 1
    assert response.status_code == 200 
    assert response.redirect_chain[-1][0] == '/agenda/'

@pytest.mark.django_db
def test_falha_por_conflito_de_horario(client, agendamento_url, agendamento_valido_data, agendamento_existente):

    dados_conflitantes = agendamento_valido_data.copy()
    dados_conflitantes['data_hora'] = agendamento_existente.data_hora.isoformat()
    
    assert Agendamento.objects.count() == 1
    
    response = client.post(agendamento_url, dados_conflitantes, follow=True)
    
    assert Agendamento.objects.count() == 1 
    
    assert response.status_code == 200 
    