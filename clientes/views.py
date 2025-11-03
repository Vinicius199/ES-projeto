from datetime import datetime, timedelta 
from django.utils import timezone 
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CadastroForm, ClienteUpdateForm, AgendamentoForm
from .models import Cliente, Agendamento, Servico, Profissional

def home(request):
    return render(request, 'home.html')
    
def fazer_login(request):
    
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

@login_required
def service(request):
    # Lógica para exibir a página de serviços (GET)
    if request.method == 'GET':
        servicos = Servico.objects.all()
        form = AgendamentoForm() 
        context = {
            'servicos': servicos,
            'form': form
        }
        return render(request, 'servico.html', context)
    
    elif request.method == 'POST':
        # O formulário AgendamentoForm espera 'Profissional', 'servico', 'data_hora'.
        # Precisamos incluir a instância 'cliente' na criação do objeto.
        
        form = AgendamentoForm(request.POST) 
        
        if form.is_valid():
            # CASO DE SUCESSO: O agendamento está OK e não há conflito
            try:
                # O form.save(commit=False) cria o objeto, mas não salva no banco ainda.
                agendamento = form.save(commit=False)
                
                # Campos adicionais antes de salvar
                agendamento.cliente = request.user 
                agendamento.confirmado = True
                
                #Agora sim salva no banco de dados
                agendamento.save() 
                
                messages.success(request, "Agendamento realizado com sucesso! 🎉")
                return redirect('agenda')

            except Exception as e:
                # Erro interno na criação/salvamento do objeto
                print(f"Erro ao salvar agendamento: {e}")
                messages.error(request, "Erro interno ao processar o agendamento.")
                
                # Ajuste: Redireciona para 'service' para mostrar erro genérico
                return redirect('service') 
                
        else:
            # CASO DE ERRO: Conflito de horário ou campo obrigatório faltando
            
            for field, errors in form.errors.items():
                for error in errors:
                    # 'error' aqui contém a mensagem de conflito de horário (ex: "Conflito de horário!...")
                    messages.error(request, f"{error}") 
            
            # Recarrega a página de serviços para mostrar as mensagens (o aviso de erro de conflito)
            return redirect('service') 
            
    return redirect('service')

def get_profissionais_por_servico(request, servico_id):
    """
    Retorna uma lista JSON dos profissionais aptos para o servico_id.
    Esta view será chamada via AJAX pelo JavaScript.
    """
   
    try:
        
        servico = get_object_or_404(Servico, pk=servico_id)
        
        # Filtra os profissionais relacionados ao serviço
        # 'profissionais_aptos' é o related_name definido no seu models.py
        profissionais = servico.profissionais_aptos.all().order_by('nome')
        
        # prints para testes: Imprima o que está sendo buscado
        #print(f"Serviço ID: {servico_id}")
        #print(f"Profissionais encontrados: {profissionais.count()}")
        
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
def cancelar_agendamento(request, agendamento_id):
    if request.method == 'POST':
        #Busca o agendamento
        agendamento = get_object_or_404(
            Agendamento, 
            pk=agendamento_id, 
            cliente=request.user
        )

        #Verifica se o agendamento já está cancelado
        if agendamento.cancelado:
            messages.warning(request, "Este agendamento já foi cancelado.")
            return redirect('agenda')

        # Obtém a hora atual com timezone
        agora = timezone.now()
        
        # Calcula o "momento limite": 15 minutos antes do agendamento(da para ajustar aqui o tempo como quiser)
        momento_limite = agendamento.data_hora - timedelta(minutes=15)
        
        # Verificação de restrição (faltam menos de 15 minutos)
        if agora >= momento_limite:
            messages.error(request, "O cancelamento só pode ser feito até 15 minutos antes do horário marcado.")
            # Redireciona SEM cancelar
            return redirect('agenda')
        
        # Atualiza o status de cancelamento
        agendamento.cancelado = True
        agendamento.confirmado = False 
        
        agendamento.save()
        
        messages.success(request, "Agendamento cancelado com sucesso.")

    return redirect('agenda')

@login_required
def cliente(request):
    # O request.user já é a instância do cliente logado (o objeto Cliente)

    if request.method == 'POST':
        #Popula o formulário com os dados POST e a instância atual do usuário
        form = ClienteUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            # Salva a instância atualizada do usuário no banco
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

