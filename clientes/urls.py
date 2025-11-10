from django.urls import path
from . import views

urlpatterns = [
    # Principais e Autenticação 
    path('home/', views.home, name='home'),
    path('login/', views.fazer_login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('sair/', views.logout, name='logout_view'),
    
    # Painel Administrativo (Listagem e Cadastro)
    path('admin-painel/', views.painel_admin, name='painel_admin'), 
    path('api/funcionarios', views.cadastrar_profissional, name='api_cadastrar_profissional'),
    path('api/servicos', views.cadastrar_servico, name='api_cadastrar_servico'),
    
    #GERENCIAMENTO DE FUNCIONÁRIOS
    path('admin-painel/funcionario/editar/<int:pk>/', views.editar_profissional, name='editar_funcionario'),
    path('admin-painel/funcionario/excluir/<int:pk>/', views.excluir_profissional, name='excluir_funcionario'),
    
    #GERENCIAMENTO DE SERVIÇOS
    path('admin-painel/servico/editar/<int:pk>/', views.editar_servico, name='editar_servico'),
    path('admin-painel/servico/excluir/<int:pk>/', views.excluir_servico, name='excluir_servico'),
    
    #Rotas de Agendamento e Perfil
    path('service/', views.service, name='service'),
    path('agenda/', views.agenda, name='agenda'),
    path('cliente/', views.cliente, name='cliente'),
    path('servico/<int:servico_id>/profissionais/', views.get_profissionais_por_servico, name='profissionais_por_servico'),
    path('agenda/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
]