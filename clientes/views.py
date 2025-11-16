from datetime import datetime, timedelta 
from django.utils import timezone 
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import CadastroForm, ClienteUpdateForm, AgendamentoForm, ProfissionalForm, ServicoForm
from .models import Cliente, Agendamento, Servico, Profissional
from django.views.decorators.http import require_POST, require_http_methods 

# Funçao auxiliar para proteger o Admin)
def is_admin_or_staff(user):
    """ Verifica se o usuário é ativo e tem permissões de staff/admin. """
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def home(request):
    return render(request, 'home.html')

@user_passes_test(is_admin_or_staff)
def painel_admin(request):
    """
    Renderiza o painel de cadastro, passando as listas de Profissionais e Serviços
    para popular as tabelas de gerenciamento nos modais.
    """
    profissionais = Profissional.objects.all().order_by('nome')
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
    form = ProfissionalForm(request.POST) 
    
    if form.is_valid():
        try:
            form.save()
            
            profissionais_atuais = Profissional.objects.all().order_by('nome')
            
            profissionais_data = [
                {'id': p.id, 'nome': p.nome, 'sobrenome': p.sobrenome} 
                for p in profissionais_atuais
            ]

            return JsonResponse({
                'status': 'sucesso', 
                'mensagem': 'Funcionário cadastrado com sucesso!', 
                'profissionais_list': profissionais_data 
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': f'Erro ao salvar: {e}'}, status=500)
    else:
        return JsonResponse({'status': 'erro', 'mensagem': 'Dados inválidos.', 'erros': form.errors}, status=400)

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
    """ Exclui um Profissional (Funcionário) e redireciona. """
    profissional = get_object_or_404(Profissional, pk=pk)
    
    try:
        profissional.delete()
        messages.success(request, f"Profissional '{profissional.get_full_name()}' excluído com sucesso!")
    except Exception as e:
        messages.error(request, f"Não foi possível excluir o profissional. Possivelmente, existem agendamentos associados. Erro: {e}")

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
            # ❗ DEBUG: Imprima os erros para diagnóstico no console do servidor
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
        # Você pode precisar adicionar outras listas (profissionais_list, servicos_list)
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
        
        if user is None:
             credenciais = {'email': email, 'password': senha}
             user = authenticate(request, **credenciais) 
             
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
    
    elif request.method == 'POST':
        form = AgendamentoForm(request.POST) 
        
        if form.is_valid():
            try:
                agendamento = form.save(commit=False)
                agendamento.cliente = request.user 
                agendamento.confirmado = True
                agendamento.save() 
                
                messages.success(request, "Agendamento realizado com sucesso! 🎉")
                return redirect('agenda')

            except Exception as e:
                print(f"Erro ao salvar agendamento: {e}")
                messages.error(request, "Erro interno ao processar o agendamento.")
                return redirect('service') 
                
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}") 
            
            return redirect('service') 
            
    return redirect('service')

def get_profissionais_por_servico(request, servico_id):
    try:
        servico = get_object_or_404(Servico, pk=servico_id)
        profissionais = servico.profissionais_aptos.all().order_by('nome') 
        
        profissionais_data = [
            {
                'id': p.id,
                'nome_completo': p.get_full_name() 
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
    professionals_data = Profissional.objects.all().values('id', 'nome', 'sobrenome')
    
    professionals_list = [
        {
            'id': prof['id'], 
            'name': f"{prof['nome']} {prof['sobrenome']}"
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