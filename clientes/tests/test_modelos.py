import pytest
from clientes.models import Agendamento
from datetime import timedelta
from dateutil import parser
from django.conf import settings
from django.utils import timezone

@pytest.mark.django_db
def test_duracao_do_agendamento_calculada(agendamento_valido_data, existing_client, servico_test, cria_um_profissional_test):
    #cria um datatime (naive) a partir da string
    data_hora_naive = parser.isoparse(agendamento_valido_data['data_hora'])
    #torna o datetime ciete do fuso horario "aware" 
    #time.make_aware converte um datetime naive em aware usando o fuso horario definido em settings
    data_hora_obj = timezone.make_aware(data_hora_naive)

    agendamento = Agendamento.objects.create(
        cliente=existing_client,
        servico=servico_test,
        Profissional=cria_um_profissional_test,
        data_hora=data_hora_obj
    )
    
    tempo_esperado = agendamento.data_hora + timedelta(minutes=servico_test.duracao_minutos)
    
    assert Agendamento.objects.count() == 1
    assert agendamento.Profissional == cria_um_profissional_test