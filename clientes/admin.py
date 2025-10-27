from django.contrib import admin
from .models import Cliente, Servico, Agendamento, Profissional

# 1. Registro do Modelo Servico
@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de Servicos
    list_display = ('nome', 'duracao_minutos')
    search_fields = ('nome',)

# 2. Registro do Modelo Agendamento
@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na lista de Agendamentos
    list_display = ('cliente', 'servico', 'data_hora')
    
    # Adiciona filtros laterais para facilitar a busca
    list_filter = ('servico', 'data_hora')
    
    # Permite buscar pelo nome do cliente ou serviço
    search_fields = ('cliente__nome', 'servico__nome')
    
# 3. Registro do Cliente (Se o Django não o fez automaticamente)
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'sobrenome', 'telefone', 'is_staff')
    search_fields = ('email', 'nome')
    list_filter = ('is_staff', 'is_superuser')

@admin.register(Profissional) # <-- REGISTRO SIMPLES
class ProfissionalAdmin(admin.ModelAdmin):
    # Exibir todos os campos importantes e a lista de serviços que ele pode fazer
    list_display = ('nome', 'sobrenome', 'email', 'telefone') 
    search_fields = ('nome', 'email')
    
    
    filter_horizontal = ('servicos',)