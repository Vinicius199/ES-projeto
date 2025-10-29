from datetime import datetime, timedelta # Adicionado timedelta para o cancelamento
from django.utils import timezone # Lida com a data e hora (usado no cancelamento)
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CadastroForm, ClienteUpdateForm 
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

#@login_required
def service(request):
    # Lógica para exibir a página de serviços (GET)
    if request.method == 'GET':
        servicos = Servico.objects.all()
        context = {'servicos': servicos}
        return render(request, 'servico.html', context)
    
    # Lógica para processar o agendamento (POST)
    elif request.method == 'POST':
        # 1. Capturar os dados que vieram do formulário oculto
        servico_id = request.POST.get('servico_id')
        data_hora_str = request.POST.get('data_hora')
        profissional_id = request.POST.get('profissional_id')
        
        # 2. Validação básica (garantir que os IDs não são vazios)
        if not all([servico_id, data_hora_str, profissional_id]):
            # Se faltar dados, retorna para a página de serviços com erro (ou exibe uma mensagem)
            # Para simplificar, vamos redirecionar:
            # messages.error(request, "Dados de agendamento incompletos.")
            return redirect('service') 

        try:
            # 3. Converter data/hora e buscar objetos
            # Lembre-se: datetime-local envia no formato 'YYYY-MM-DDTHH:MM'
            from datetime import datetime
            data_hora_agendamento = datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M')
            
            servico = Servico.objects.get(pk=servico_id)
            profissional = Profissional.objects.get(pk=profissional_id)
            cliente = request.user # O cliente é o usuário logado

            # 4. Salvar o agendamento no banco de dados
            Agendamento.objects.create(
                cliente=cliente,
                servico=servico,
                Profissional=profissional,
                data_hora=data_hora_agendamento,
                confirmado=True
            )
            
            #REDIRECIONAR PARA A PÁGINA 'agenda' APÓS O SUCESSO!
            # messages.success(request, "Agendamento realizado com sucesso!")
            return redirect('agenda') # <-- A SOLUÇÃO FINAL

        except Exception as e:
            # Se a busca de objetos falhar (ID inválido, por exemplo)
            print(f"Erro ao salvar agendamento: {e}")
            # messages.error(request, "Erro ao processar seu agendamento. Tente novamente.")
            return redirect('service')


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
        
        # Calcula o "momento limite": 15 minutos antes do agendamento
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

