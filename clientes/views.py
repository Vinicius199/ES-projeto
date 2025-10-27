import datetime
from django.utils import timezone #lida com a data e hora
from django.shortcuts import get_object_or_404, render, redirect
from .forms import CadastroForm, ClienteUpdateForm, LoginForm 
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from .models import Cliente, Agendamento, Servico, Profissional
from . import views
import re

def home(request):
    return render(request, 'home.html')
    
def fazer_login(request): # Certifique-se de que este nome está no seu urls.py
    
    # Redireciona se já estiver autenticado
    if request.user.is_authenticated:
        return redirect('home') 

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        user = authenticate(request, username=email, password=senha)
        
        # Se a autenticação falhar, tenta passar as credenciais diretamente, 
        #    usando 'email' (o nome real do campo no seu modelo).
        if user is None:
             credenciais = {'email': email, 'password': senha}
             # Força a autenticação passando o dicionário de credenciais
             user = authenticate(request, **credenciais) 
             
        # --- FIM DA AUTENTICAÇÃO ---

        if user is not None:
            # Sucesso: Loga o usuário
            django_login(request, user) 
            
            # Redirecionamento (mantido do seu código original)
            next_url = request.POST.get('next') or request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # Falha: Credenciais inválidas
            messages.error(request, "E-mail ou senha inválidos. Tente novamente.")
            return render(request, 'login.html', {'email_digitado': email})
    
    # GET request
    return render(request, 'login.html')

@csrf_exempt
def cadastro(request): 
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        
        if form.is_valid():
            form.save() # O save() já faz o hashing
            messages.success(request, "Cadastro realizado com sucesso! \nFaça seu login.")
            return redirect('login') 
            
        else:
            # Erro de validação: retorna o formulário com os erros anexados.
            messages.error(request, "Houve erros na validação. Verifique os campos.")
            return render(request, 'cadastro.html', {'form': form})
            
    else:
        form = CadastroForm()
        return render(request, 'cadastro.html', {'form': form})

#@login_required
def service(request):
    # Obtém a lista de serviços do Banco de Dados para exibir
    servicos = Servico.objects.all() 
    
    if request.method == 'POST':

        servico_id = request.POST.get('servico_id')
        data_hora_str = request.POST.get('data_hora') 
        profissional_id = request.POST.get('profissional_id') 

        if not all([servico_id, data_hora_str, profissional_id]):
            messages.error(request, "Todos os campos (Serviço, Profissional, Data/Hora) são obrigatórios.")
            return redirect('service')

        try:
            # 1. Busca os objetos pelo ID
            servico = Servico.objects.get(pk=servico_id)
            profissional = Profissional.objects.get(pk=profissional_id) # <-- BUSCA O PROFISSIONAL
            
            # 2. Converte a string de data/hora para um objeto datetime (NAIVE)
            data_hora_naive = timezone.datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')
            data_hora_agendamento = timezone.make_aware(data_hora_naive)
            
            # 3. VALIDAÇÃO DO HORÁRIO NO PASSADO
            if data_hora_agendamento < timezone.now():
                messages.error(request, "Não é possível agendar horários no passado. Por favor, escolha uma data e hora futuras.")
                return redirect('service') 
            
            # 4. Verifica se o profissional E o horário já estão ocupados
            # A verificação deve ser mais rigorosa: conflito para o MESMO PROFISSIONAL
            conflito = Agendamento.objects.filter(
                profissional=profissional, # <-- NOVO: Verifica conflito apenas para o profissional escolhido
                data_hora=data_hora_agendamento
            ).exists()
            
            if conflito:
                messages.error(request, f"O horário das {data_hora_agendamento.strftime('%H:%M')} já está reservado para {profissional.nome}. Escolha outro.")
                return redirect('service')

            # 5. SALVAR NO BANCO DE DADOS
            Agendamento.objects.create(
                cliente=request.user, 
                servico=servico,
                profissional=profissional, # <-- NOVO: SALVA O PROFISSIONAL
                data_hora=data_hora_agendamento # Salva o objeto AWARE corrigido
            )
            
            messages.success(request, f"Agendamento de {servico.nome} com {profissional.nome} realizado para {data_hora_agendamento.strftime('%d/%m/%Y às %H:%M')}!")
            return redirect('agenda') 
            
        except Servico.DoesNotExist:
            messages.error(request, "Serviço inválido.")
        except Profissional.DoesNotExist: # <-- NOVO
            messages.error(request, "Profissional inválido.")
        except ValueError:
            messages.error(request, "Formato de data e hora inválido. Certifique-se de preencher ambos os campos.")
        except Exception as e:
            print("ERRO DE SALVAMENTO DETECTADO:", e)
            messages.error(request, f"Ocorreu um erro inesperado ao agendar: {e}")

    # Renderiza a tela de serviços (GET Request)
    return render(request, 'servico.html', {'servicos': servicos})

def get_profissionais_por_servico(request, servico_id):
    """
    Retorna uma lista JSON dos profissionais aptos para o servico_id.
    Esta view será chamada via AJAX pelo JavaScript.
    """
    # É uma boa prática proteger views de API/AJAX para que apenas chamadas AJAX as usem
    #if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #    return JsonResponse({'error': 'Requisição inválida.'}, status=400)
    
    try:
        # Encontra o serviço ou retorna erro 404
        # Note: get_object_or_404 foi importado no topo
        servico = get_object_or_404(Servico, pk=servico_id)
        
        # Filtra os profissionais relacionados ao serviço
        # 'profissionais_aptos' é o related_name definido no seu models.py
        profissionais = servico.profissionais_aptos.all().order_by('nome')
        
        # 💡 DEBUG: Imprima o que está sendo buscado
        print(f"Serviço ID: {servico_id}")
        print(f"Profissionais encontrados: {profissionais.count()}")
        
        # Prepara os dados para o JavaScript
        profissionais_data = [
            {
                'id': p.id,
                'nome_completo': p.nome # Assume que você tem o método get_full_name
            }
            for p in profissionais
        ]
        
        return JsonResponse({'profissionais': profissionais_data})
    
    except Exception as e:
        return JsonResponse({'error': f'Erro ao buscar dados: {str(e)}'}, status=500)

def logout(request):
    django_logout(request)
    return redirect('home')

@login_required
def agenda(request):
    # Filtra APENAS os agendamentos do usuário logado e ordena por data
    meus_agendamentos = Agendamento.objects.filter(
        cliente=request.user
    ).select_related('servico').order_by('data_hora')
    
    context = {
        'agendamentos': meus_agendamentos
    }
    return render(request, 'agenda.html', context)

@login_required
def cliente(request):
    # O request.user já é a instância do cliente logado (o objeto Cliente)

    if request.method == 'POST':
        # 1. Popula o formulário com os dados POST e a instância atual do usuário
        form = ClienteUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            # 2. Salva a instância atualizada do usuário no banco
            form.save()
            messages.success(request, 'Seus dados foram atualizados com sucesso! ✅')
            return redirect('cliente')
        else:
            messages.error(request, 'Houve um erro ao atualizar os dados. Verifique os campos.')
            
    else:
        # GET Request: Preenche o formulário com os dados atuais do usuário
        form = ClienteUpdateForm(instance=request.user)
        
    context = {
        'form': form,
    }
    return render(request, 'cliente.html', context)