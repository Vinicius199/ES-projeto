from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm 
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib import messages
import json
from .models import Cliente
from . import views
import re

def home(request):
    return render(request, 'home.html')
    
def login(request):
    if request.user.is_authenticated:
        return redirect('home') # Redireciona se já estiver logado

    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # O authenticate() lida com a verificação da senha hasheada!
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            # Loga o usuário
            django_login(request, user) 
            
            # Use o parâmetro 'next' para redirecionar para a página anterior, se houver.
            next_url = request.POST.get('next') or request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            # Credenciais inválidas
            messages.error(request, "E-mail ou senha inválidos. Tente novamente.")
            
            # Retorna o formulário com o campo 'email' preenchido para conveniência
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
    
def service(request):
    return render(request, 'servico.html')

def logout(request):
    django_logout(request)
    return redirect('home')
    