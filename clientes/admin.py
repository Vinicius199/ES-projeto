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

@admin.register(Profissional)
class ProfissionalAdmin(admin.ModelAdmin):
    list_display = (
        'user_nome_completo', 
        'user_email', 
        'user_telefone', 
        'num_servicos_aptos' 
    ) 
    
    search_fields = (
        'user__nome',
        'user__sobrenome',
        'user__email',
        'user__telefone',
    )
    
    filter_horizontal = ('servicos',)
    
    
    @admin.display(description='Nome Completo')
    def user_nome_completo(self, obj):
        return obj.user.get_full_name()
    
    @admin.display(description='E-mail')
    def user_email(self, obj):
        return obj.user.email
        
    @admin.display(description='Telefone')
    def user_telefone(self, obj):
        return obj.user.telefone
        
    @admin.display(description='Serviços Aptos')
    def num_servicos_aptos(self, obj):
        return obj.servicos.count()