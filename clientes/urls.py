from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.fazer_login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('sair/', views.logout, name='logout_view'),

    path('auth/google/', views.google_calendar_auth_start, name='google_calendar_auth_start'),
    path('auth/google/callback/', views.google_calendar_auth_callback, name='google_calendar_auth_callback'),
    path('', views.google_calendar_auth_callback, name='google_calendar_desktop_callback'),
    
    path('admin-painel/', views.painel_admin, name='painel_admin'),
    path('api/funcionarios', views.cadastrar_profissional, name='api_cadastrar_profissional'),
    path('api/funcionarios/com_login', views.cadastrar_profissional, name='api_cadastrar_profissional_com_login'),
    path('api/servicos', views.cadastrar_servico, name='api_cadastrar_servico'),
    path('api/agendamentos-profissionais/', views.get_professional_schedules, name='api_schedules'),
    path('excluir-conta/', views.excluir_conta, name='excluir_conta'),

    path('admin-painel/funcionario/editar/<int:pk>/', views.editar_profissional, name='editar_funcionario'),
    path('admin-painel/funcionario/excluir/<int:pk>/', views.excluir_profissional, name='excluir_funcionario'),
    
    path('admin-painel/servico/editar/<int:pk>/', views.editar_servico, name='editar_servico'),
    path('admin-painel/servico/excluir/<int:pk>/', views.excluir_servico, name='excluir_servico'),
    
    path('service/', views.service, name='service'),
    path('agenda/', views.agenda, name='agenda'),
    path('cliente/', views.cliente, name='cliente'),
    
    path('agendar/', views.criar_agendamento, name='criar_agendamento'), 
    
    path('servico/<int:servico_id>/profissionais/', views.get_profissionais_por_servico, name='get_profissionais_por_servico'),
    path('agenda/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
]