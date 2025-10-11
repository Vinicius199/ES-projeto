from django.shortcuts import render, redirect
import datetime
from django.http import HttpResponse
from .models import Cliente
import re
import os
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build


def clientes(request):
    #return render(request, 'cliente.html') #o render esta buscando o arquivo clientes.html na pasta templetes de fora do app clientes 
    #return render(request, 'cliente.html') 

    if request.method == 'GET':
        return render(request, 'cliente.html')
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        senha = request.POST.get('senha')

    cliente = Cliente(
        nome=nome, 
        sobrenome=sobrenome,
        email=email,
        telefone=telefone, 
        senha=senha)
        
    Cliente.save()

    clientes = Cliente.objects.filter(telefone=telefone)

    if clientes.exists():
        return render(request, 'cliente.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'senha': senha})
    
    if not re.fullmatch(re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'), email):
        return render(request, 'cliente.html', {'nome': nome, 'sobrenome': sobrenome, 'telefone': telefone, 'senha': senha})
    
# Caminho do arquivo de credenciais do Google/autenticação OAuth 2.0
GOOGLE_CLIENT_SECRET_FILE = os.path.join(settings.BASE_DIR, "credentials.json")
SCOPES = ['https://www.googleapis.com/auth/calendar']

def google_login(request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/oauth2callback/"
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    request.session['flow'] = flow.authorization_url()[1]
    return redirect(auth_url)

def oauth2callback(request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri="http://localhost:8000/oauth2callback/"
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('calendar_events')

def calendar_events(request):
    if 'credentials' not in request.session:
        return redirect('google_login')

    creds = Credentials(**request.session['credentials'])
    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return render(request, 'events.html', {'events': events})

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }