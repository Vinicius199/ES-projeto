from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.fazer_login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('service/', views.service, name='service'),
    path('sair/', views.logout, name='logout_view'),
    path('agenda/', views.agenda, name='agenda'),
    path('cliente/', views.cliente, name='cliente'),
    path('servico/<int:servico_id>/profissionais/', views.get_profissionais_por_servico, name='profissionais_por_servico'),
    path('agenda/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    
    #path("google_login/", views.google_login, name="google_login"),
    #path("oauth2callback/", views.oauth2callback, name="oauth2callback"),
    #path("calendar/", views.calendar_events, name="calendar_events"),
    #path('login/', views.login, name='login'),
    #path('singup/', views.signup, name='signup'),

]