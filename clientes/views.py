from django.shortcuts import render, redirect
from .forms import CadastroForm, LoginForm 
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login
import json
from .models import Cliente
from . import views
import re

def home(request):
    return render(request, 'home.html')
    
def login(request):
    #return render(request, 'login.html')
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

    login = Cliente.objects.filter(email=email, senha=senha)
    if login.exists():
        return render(request, 'home.html')
    else:
        return render(request, 'login.html', {'email': email})

def login_api(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            cliente = Cliente.objects.filter(email=email).first()
            if cliente and cliente.check_password(senha):  # Verifica a senha
                django_login(request, cliente)  # Cria a sessão de login
                return JsonResponse({'success': True, 'message': 'Login realizado com sucesso!'})
            else:
                return JsonResponse({'success': False, 'message': 'Email ou senha incorretos.'})
        else:
            errors = form.errors.get_json_data()
            return JsonResponse({'success': False, 'errors': errors})

@csrf_exempt
def cadastro_api(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()
            print("Cadastro realizado com sucesso!")
            return JsonResponse({'message': 'Cadastro realizado com sucesso!', 'redirect_url': '/login/'}, status=201)
        else:
            print("Erro no formulário:", form.errors)
            return render(request, 'cadastro.html', {'form': form, 'errors': 'formulario invalido'})
    else:
        form = CadastroForm()
        return render(request, 'cadastro.html', {'form': form})
    
def service(request):
    return render(request, 'servicoteteste.html')
    