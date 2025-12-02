import json, os
from pathlib import Path
from datetime import datetime, timedelta 
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone 
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CadastroForm, ClienteUpdateForm, AgendamentoForm, ProfissionalForm, ServicoForm, ProfissionalCadastroForm
from .models import Cliente, Agendamento, Servico, Profissional
from django.views.decorators.http import require_POST, require_http_methods
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parent.parent

#Configuração do google calendar
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'config', 'credentials.json')

#permissões basicas de acesso ao calendário
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'openid',
    'email',
    'profile'
]
#vericação de segurança
if not os.path.exists(CLIENT_SECRET_FILE):
    print("Arquivo de credenciais do Google não encontrado em: {CLIENT_SECRET_FILE} ")

# Funçao auxiliar para proteger o Admin)
def is_admin_or_staff(user):
    """ Verifica se o usuário é ativo e tem permissões de staff/admin. """
    return user.is_authenticated and (user.is_staff or user.is_superuser)

#autenticação do auth google calendar
@login_required
def google_calendar_auth_start(request):

    relative_path = reverse('google_calendar_auth_callback')

    callback_uri = request.build_absolute_uri(relative_path)
    #callback_uri = "http://127.0.0.1:8000/"


    if callback_uri.startswith('https'):
        callback_uri = callback_uri.replace('https', 'http', 1)

    print(f"DEBUG: URL enviada final: {callback_uri}")

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, 
        scopes=SCOPES, 
        redirect_uri=callback_uri
        #request.build_absolute_uri('callback') 
    )

    flow.redirect_uri = callback_uri

    authorization_url, state = flow.authorization_url(
        access_type='offline', 
        include_granted_scopes='true'
    )
    
    request.session['oauth_state'] = state
    request.session['oauth_cliemt_id'] = flow.client_config['client_id']
    
    return redirect(authorization_url)

@login_required
def google_calendar_auth_callback(request):

    state = request.session.pop('oauth_state', None)
    
    if not state or state != request.GET.get('state'):
        print(f"ERRO STATE: Sessão '{state}' vs Google '{request.GET.get('state')}'")
        messages.error(request, "Erro de segurança (STATE mismatch). Tente novamente.")
        return redirect('cliente') 

    try:
        
        authorization_response = request.build_absolute_uri()

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_FILE, 
            scopes=SCOPES, 
            redirect_uri=request.build_absolute_uri(reverse('google_calendar_auth_callback')),
            #redirect_uri=request.build_absolute_uri() # Usa a URL atual
        )
        #flow.redirect_uri = 'http://127.0.0.1:8000/'

        #query_string = request.get_full_path()
        #authorization_response_url = f"http://127.0.0.1:8000/{query_string}"
        #flow.fetch_token(authorization_response=authorization_response_url)
        
        authorization_response_url = request.build_absolute_uri()

        if authorization_response_url.startswith('https'):
            authorization_response = authorization_response_url.replace('https', 'http', 1)
        
        flow.fetch_token(authorization_response=authorization_response)

        refresh_token = flow.credentials.refresh_token
        
        # Salva o Refresh Token no modelo do Cliente
        cliente = request.user
        cliente.google_refresh_token = refresh_token
        cliente.save()
        
        messages.success(request, "✅ Acesso ao Google Agenda autorizado com sucesso! Você pode agendar serviços agora.")

    except Exception as e:
        print(f"Erro ao processar callback do Google: {e}")
        messages.error(request, f"❌ Não foi possível autorizar o Google Agenda. Verifique as credenciais. Erro: {e}")
        
    return redirect('cliente')

def create_calendar_event(cliente, service_name, professional_name, start_time, duration_minutes):
    
    if not cliente.google_refresh_token:
        print(f"Cliente {cliente.email} não autorizou o Google Calendar.")
        return None
        
    try:
        with open(CLIENT_SECRET_FILE, 'r') as token:
             client_secrets = json.load(token)['web']
             
        creds = Credentials(
            None, 
            refresh_token=cliente.google_refresh_token,
            token_uri=client_secrets['token_uri'],
            client_id=client_secrets['client_id'],
            client_secret=client_secrets['client_secret'],
            scopes=SCOPES
        )
        
        # Renove o Access Token (se expirado)
        creds.refresh(Request())
            
        service = build('calendar', 'v3', credentials=creds)

    except Exception as e:
        print(f"Erro ao autenticar/renovar token do Google Calendar: {e}")
        return None

    TIMEZONE = 'America/Sao_Paulo'
    
    start_time_local = start_time.astimezone(timezone.get_current_timezone())
    end_time = start_time_local + timedelta(minutes=duration_minutes)

    event = {
        'summary': f'{service_name} com {professional_name}',
        'description': f'Agendamento de {service_name} com o profissional {professional_name}.',
        'start': {
            'dateTime': start_time_local.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': TIMEZONE,
        },
        'attendees': [
            {'email': cliente.email, 'responseStatus': 'accepted'}, 
        ],
        'status': 'confirmed',
        'reminders': {'useDefault': True},
    }

    try:
        # Cria o evento na agenda principal do cliente
        event = service.events().insert(
            calendarId='primary', 
            sendNotifications=True, # Envia notificação por e-mail para o cliente
            body=event
        ).execute()

        print(f"Evento criado no Google Agenda: {event.get('htmlLink')}")
        return event.get('id')

    except Exception as e:
        print(f"Erro ao criar evento do Google Calendar: {e}")
        return None

def home(request):
    return render(request, 'home.html')

@user_passes_test(is_admin_or_staff)
def painel_admin(request):
    
    profissionais = Profissional.objects.all().order_by('user__nome')
    servicos = Servico.objects.all().order_by('nome')
    
    context = {
        'profissionais_list': profissionais, # Lista de profissionais (para o form de Serviço)
        'funcionarios_list': profissionais,  # Lista de funcionários (para o modal de listagem)
        'servicos_list': servicos,           # Lista de serviços (para o modal de listagem)
    }
    return render(request, 'admin.html', context) 

@require_POST
@user_passes_test(is_admin_or_staff, login_url='login')
def cadastrar_profissional(request):
    
    nome = request.POST.get('nome')
    sobrenome = request.POST.get('sobrenome')
    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    senha = request.POST.get('senha')
    
    is_staff_admin = request.POST.get('is_staff') == 'on' 

    telefone_limpo = ''.join(filter(str.isdigit, telefone)) if telefone else ''

    erros = {}
    if not nome:
        erros['nome'] = ['O nome é obrigatório.']
    if not sobrenome:
        erros['sobrenome'] = ['O sobrenome é obrigatório.']
    if not email:
        erros['email'] = ['O e-mail é obrigatório.']
    if not senha:
        erros['senha'] = ['A senha é obrigatória.']
    
    try:
        if Cliente.objects.filter(email=email).exists():
            erros['email'] = ["Este e-mail já está cadastrado. Por favor, use outro."]
    except NameError:
         pass 

    if erros:
        return JsonResponse({
            'status': 'erro', 
            'mensagem': 'Dados inválidos. Por favor, corrija os erros detalhados.', 
            'erros': erros
        }, status=400)
    
    try:
        novo_cliente = Cliente.objects.create_user(
            email=email,
            password=senha,
            nome=nome,
            sobrenome=sobrenome,
            telefone=telefone_limpo,
            is_staff=is_staff_admin, 
            is_active=True 
        )
        if is_staff_admin:
            novo_cliente.is_superuser = True
            novo_cliente.save()
        
        profissional = Profissional.objects.create(
            user=novo_cliente,
        )
        profissionais_atuais = Profissional.objects.all().order_by('user__nome')
        profissionais_data = [
            {'id': p.pk, 'nome': p.user.nome, 'sobrenome': p.user.sobrenome, 'email': p.user.email} 
            for p in profissionais_atuais
        ]
        
        acesso_admin_msg = "com acesso Admin." if is_staff_admin else "como funcionário normal."

        return JsonResponse({
            'status': 'sucesso', 
            'mensagem': f"Funcionário {novo_cliente.get_full_name()} cadastrado com sucesso {acesso_admin_msg}!", 
            'profissionais_list': profissionais_data 
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'status': 'erro', 'mensagem': f'Erro ao salvar: {e}'}, status=500)

@require_POST
@user_passes_test(is_admin_or_staff, login_url='login')
def api_cadastrar_profissional_com_login(request):
    
    nome = request.POST.get('nome')
    sobrenome = request.POST.get('sobrenome')
    email = request.POST.get('email')
    telefone = request.POST.get('telefone')
    senha = request.POST.get('senha')
    
    is_staff_admin = request.POST.get('is_staff') == 'on' 

    telefone_limpo = ''.join(filter(str.isdigit, telefone)) if telefone else ''

    erros = {}
    if not nome:
        erros['nome'] = 'O nome é obrigatório.'
    if not email:
        erros['email'] = 'O e-mail é obrigatório.'
    if not senha:
        erros['senha'] = 'A senha é obrigatória.'
    
    if Cliente.objects.filter(email=email).exists():
        erros['email'] = "Este e-mail já está cadastrado. Por favor, use outro."
        
    if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
        erros['telefone'] = "Telefone deve ter 10 ou 11 dígitos, incluindo o DDD."
        
    if erros:
        return JsonResponse({
            'status': 'erro', 
            'mensagem': 'Dados inválidos.', 
            'erros': erros
        }, status=400)
        
    try:
        novo_cliente = Cliente.objects.create_user(
            email=email,
            password=senha,
            nome=nome,
            sobrenome=sobrenome,
            telefone=telefone_limpo,

            is_staff=is_staff_admin,
            is_active=True 
        )

        Profissional.objects.create(
            user=novo_cliente 
        )
        
        profissionais_atuais = Profissional.objects.all().order_by('user__nome')
        profissionais_data = [
            {'id': p.pk, 'nome': p.user.get_full_name(), 'email': p.user.email} 
            for p in profissionais_atuais
        ]
        
        acesso_admin_msg = "com acesso Admin." if is_staff_admin else "como funcionário normal."

        return JsonResponse({
            'status': 'sucesso', 
            'mensagem': f"Funcionário {novo_cliente.get_full_name()} cadastrado com sucesso {acesso_admin_msg}!", 
            'profissionais_list': profissionais_data
        }, status=201)
        
    except Exception as e:
        return JsonResponse({'status': 'erro', 'mensagem': f'Erro interno ao salvar: {e}'}, status=500)

@require_POST
@user_passes_test(is_admin_or_staff, login_url='login')
def cadastrar_servico(request):
    
    dados_post = request.POST.copy()
    
    if 'tempo' in dados_post:
        try:
            tempo_str = dados_post.get('tempo')
            if len(tempo_str.split(':')) == 2:
                horas, minutos = map(int, tempo_str.split(':'))
                duracao_minutos = (horas * 60) + minutos
                
                dados_post['duracao_minutos'] = duracao_minutos
                
        except ValueError:
            pass

    form = ServicoForm(dados_post)
    
    if form.is_valid():
        try:
            servico = form.save() 
            
            profissionais_ids = request.POST.getlist('profissionais')
            
            servico.profissionais_aptos.set(profissionais_ids) 
            
            return JsonResponse({
                'status': 'sucesso', 
                'mensagem': 'Serviço e profissionais associados cadastrados com sucesso!'
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': f'Erro ao salvar serviço: {e}'}, status=500)
    else:
        return JsonResponse({
            'status': 'erro', 
            'mensagem': 'Dados inválidos.', 
            'erros': form.errors
        }, status=400)

@require_POST 
@user_passes_test(is_admin_or_staff) 
def excluir_profissional(request, pk):
    
    profissional = get_object_or_404(Profissional, pk=pk)
    
    nome_completo = profissional.user.get_full_name()
    cliente_user = profissional.user 

    try:
        with transaction.atomic():
            
            profissional.delete()
            
            cliente_user.delete() 
            
            messages.success(request, f"O funcionário **{nome_completo}** foi excluído com sucesso.")
            
    except IntegrityError:
        messages.error(request, f"Não foi possível excluir **{nome_completo}**. Ele(a) possui registros associados (como agendamentos) que precisam ser removidos primeiro.")
        
    except Exception as e:
        messages.error(request, f"Erro inesperado ao excluir o funcionário: {e}")

    return redirect('painel_admin')

@require_POST
@user_passes_test(is_admin_or_staff, login_url='login')
def excluir_servico(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    nome_servico = servico.nome
    
    agendamentos_ativos = Agendamento.objects.filter(
        servico=servico,
        data_hora__gte=timezone.now(),  
        cancelado=False                 
    ).exists()

    if agendamentos_ativos:
        messages.error(
            request, 
            f"Não foi possível excluir o serviço '{nome_servico}'. Existem agendamentos ativos ou futuros vinculados a ele."
        )
        return redirect('painel_admin')
    
    try:
        servico.delete()
        messages.success(request, f"Serviço '{nome_servico}' excluído com sucesso! Agendamentos antigos foram mantidos no histórico.")
        
    except Exception as e:
        messages.error(
            request, 
            f"Ocorreu um erro ao tentar excluir o serviço. Tente novamente ou verifique logs. Erro: {e}"
        )
        
    return redirect('painel_admin')

@require_http_methods(["GET", "POST"])
@user_passes_test(is_admin_or_staff)
def editar_profissional(request, pk):
    profissional = get_object_or_404(Profissional, pk=pk)
    
    if request.method == 'POST':
        
        dados_post = request.POST.copy()
        
        if 'telefone' in dados_post and dados_post['telefone']:
            # Filtra e junta apenas os dígitos
            dados_post['telefone'] = ''.join(filter(str.isdigit, dados_post['telefone']))
        
        # Passa os dados LIMPOS para o formulário
        form = ProfissionalForm(dados_post, instance=profissional) 
        
        if form.is_valid():
            form.save()
            messages.success(request, f"Profissional '{profissional.get_full_name()}' atualizado com sucesso!")
            return redirect('painel_admin')
        else:
            # DEBUG: Imprima os erros para diagnóstico no console do servidor
            print("\n--- ERROS DE VALIDAÇÃO DO FORMULÁRIO PROFISSIONAL ---")
            print(form.errors)
            print("------------------------------------------------------\n")
            
            messages.error(request, "Erro na validação. Verifique os campos.")
            
    else: # GET
        form = ProfissionalForm(instance=profissional)
        
    context = {
        'form': form,
        'is_editing': True,
        'profissional': profissional,
    }
    
    return render(request, 'admin.html', context)

@require_http_methods(["GET", "POST"])
@user_passes_test(is_admin_or_staff)
def editar_servico(request, pk):
    servico = get_object_or_404(Servico, pk=pk)
    
    if request.method == 'POST':
        form = ServicoForm(request.POST, instance=servico) 
        
        if form.is_valid():
            servico = form.save()
            
            profissionais_ids = request.POST.getlist('profissionais')
            
            servico.profissionais_aptos.set(profissionais_ids)
            
            messages.success(request, f"Serviço '{servico.nome}' atualizado com sucesso!")
            return redirect('painel_admin')
        else:
            messages.error(request, "Erro na validação. Verifique os campos.")
            
    else: 
        form = ServicoForm(instance=servico)
        
    profissionais_list = Profissional.objects.all()

    context = {
        'form': form,
        'is_editing': True,
        'servico': servico,
        'profissionais_list': profissionais_list 
    }

    return render(request, 'admin.html', context)

def fazer_login(request):
    
    if request.user.is_authenticated:
        return redirect('home') 

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        user = authenticate(request, username=email, password=senha)
                     
        if user is not None:
            django_login(request, user) 
            
            next_url = request.POST.get('next') or request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "E-mail ou senha inválidos. Tente novamente.")
            return render(request, 'login.html', {'email_digitado': email})
    
    return render(request, 'login.html')

@csrf_exempt
def cadastro(request): 
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso! \nFaça seu login.")
            return redirect('login') 
            
        else:
            messages.error(request, "Houve erros na validação. Verifique os campos.")
            return render(request, 'cadastro.html', {'form': form})
            
    else:
        form = CadastroForm()
        return render(request, 'cadastro.html', {'form': form})

def logout(request):
    django_logout(request)
    return redirect('home')

@login_required
def cliente(request):
    if request.method == 'POST':
        form = ClienteUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Seus dados foram atualizados com sucesso! ✅')
            return redirect('cliente')
        else:
            messages.error(request, 'Houve um erro ao atualizar os dados. Verifique os campos.')
            
    else:
        form = ClienteUpdateForm(instance=request.user)
        
    context = {
        'form': form,
    }
    return render(request, 'cliente.html', context)

@login_required
def service(request):
    if request.method == 'GET':
        servicos = Servico.objects.all()
        form = AgendamentoForm() 
        context = {
            'servicos': servicos,
            'form': form
        }
        return render(request, 'servico.html', context)
        
    return redirect('service')

@login_required
def get_profissionais_por_servico(request, servico_id):
    try:
        servico = get_object_or_404(Servico, pk=servico_id)
        profissionais = servico.profissionais_aptos.all().select_related('user').order_by('user__nome') 
        
        profissionais_data = [
            {
                'id': p.id,
                'nome_completo': f"{p.user.nome} {p.user.sobrenome}".strip() or p.user.email or f"Profissional ID {p.id}",
                'email': p.user.email or "",
                'telefone': getattr(p.user, 'telefone', ''),
            }
            for p in profissionais
        ]
        
        return JsonResponse({'profissionais': profissionais_data})
    
    except Exception as e:
        return JsonResponse({'error': f'Erro ao buscar dados: {str(e)}'}, status=500)

@login_required
def agenda(request):
    meus_agendamentos = Agendamento.objects.filter(
        cliente=request.user
    ).select_related('servico', 'Profissional').order_by('data_hora')
    
    context = {
        'agendamentos': meus_agendamentos,
        'agora': timezone.now(),
    }
    return render(request, 'agenda.html', context)

@login_required
def get_professional_schedules(request):
    professionals_data = Profissional.objects.all().values('id', 'user__nome', 'user__sobrenome')
    
    professionals_list = [
        {
            'id': prof['id'], 
            'name': f"{prof['user__nome']} {prof['user__sobrenome']}"
        } 
        for prof in professionals_data
    ]

    future_schedules = Agendamento.objects.filter(
        cancelado=False, 
        data_hora__gte=timezone.now()
    ).select_related('servico', 'Profissional').order_by('data_hora')

    schedules_by_prof = {}
    for agendamento in future_schedules:
        prof_id = agendamento.Profissional.id 
        
        schedule_item = {
            'datetime': agendamento.data_hora.isoformat(),
            'service_name': agendamento.servico.nome,
            'client_name': agendamento.cliente.get_full_name(),
            'status': 'Confirmado' if agendamento.confirmado else 'Pendente',
            'id': agendamento.id
        }
        
        if prof_id not in schedules_by_prof:
            schedules_by_prof[prof_id] = []
        
        schedules_by_prof[prof_id].append(schedule_item)

    # Retorna os dados em um único JSON
    return JsonResponse({
        'professionals': professionals_list,
        'schedules': schedules_by_prof
    })

@login_required
def cancelar_agendamento(request, agendamento_id):
    if request.method == 'POST':
        agendamento = get_object_or_404(
            Agendamento, 
            pk=agendamento_id, 
            cliente=request.user
        )

        if agendamento.cancelado:
            messages.warning(request, "Este agendamento já foi cancelado.")
            return redirect('agenda')

        agora = timezone.now()
        
        # 15 minutos antes do agendamento
        momento_limite = agendamento.data_hora - timedelta(minutes=15)
        
        if agora >= momento_limite:
            messages.error(request, "O cancelamento só pode ser feito até 15 minutos antes do horário marcado.")
            return redirect('agenda')
        
        agendamento.cancelado = True
        agendamento.confirmado = False 
        
        agendamento.save()
        
        messages.success(request, "Agendamento cancelado com sucesso.")

    return redirect('agenda')

@require_POST
@login_required
def criar_agendamento(request):
    
    form = AgendamentoForm(request.POST) 
    
    if form.is_valid():
        try:
            agendamento = form.save(commit=False)
            agendamento.cliente = request.user 
            agendamento.confirmado = True
            agendamento.save()

            
            # Tenta criar o evento no Google Calendar
            cliente = request.user

            if cliente.google_refresh_token:

                servico_nome = agendamento.servico.nome
                profissional_nome = agendamento.Profissional.get_full_name()
                data_hora_inicio = agendamento.data_hora
                duracao_minutos = agendamento.servico.duracao_minutos

                evento_id = create_calendar_event(
                    cliente,
                    servico_nome,
                    profissional_nome,
                    data_hora_inicio,
                    duracao_minutos
                )

                if evento_id:
                    agendamento.google_event_id = evento_id
                    agendamento.save()
                    messages.success(request, "Agendamento realizado com o Google Agenda! 📅")
                else:
                    messages.warning(request, "Agendamento realizado, mas não foi possível criar o evento no Google Agenda.")
            else:          
                messages.success(request, "Agendamento realizado com sucesso! 🎉")
            return redirect('agenda')

        except Exception as e:
            print(f"Erro ao salvar agendamento: {e}")
            messages.error(request, f"Erro interno ao processar o agendamento. Detalhe: {e}")
            return redirect('service') 
            
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"Erro no agendamento: {error}")
        
        return redirect('service')

