from django.core.exceptions import ValidationError
import re 
from django import forms
from django.db.models import Q
from datetime import timedelta, time
from django.utils import timezone
from .models import Cliente, Agendamento, Profissional, Servico

class CadastroForm(forms.ModelForm):
    # Campo 'senha' que aparecerá no formulário
    senha = forms.CharField(
        label='Senha', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Senha', 'type':'password'})
    )
    
    class Meta:
        model = Cliente
        fields = ['nome', 'sobrenome', 'telefone', 'email', 'senha'] 
        widgets = {
             'nome': forms.TextInput(attrs={'placeholder': 'Seu Nome'}),
             'sobrenome': forms.TextInput(attrs={'placeholder': 'Sobrenome'}),
             'telefone': forms.TextInput(attrs={'placeholder': 'Telefone'}),
             'email': forms.EmailInput(attrs={'placeholder': 'E-mail'}),
        }
    
    # Validação do E-mail (se já existe)
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    #validação de Telefone
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone = re.sub(r'\D', '', telefone)
        if len(telefone) < 10 or len(telefone) > 11:
             raise ValidationError("O número de telefone deve ter 10 ou 11 dígitos, incluindo o DDD.")
        ddd = telefone[:2]
        if not re.match(r'^[1-9][0-9]$', ddd):
             raise ValidationError("O DDD deve ser válido (exemplo: 11 para São Paulo).")
        return telefone

    # Sobrescrever save() para HASHING**
    def save(self, commit=True):
        user = super().save(commit=False)
        senha_plana = self.cleaned_data["senha"]
        user.set_password(senha_plana) # HASHING AQUI!
        if commit:
            user.save()
        return user
   
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput, max_length=50)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        senha = cleaned_data.get('senha')

        if email and senha:
            user = Cliente.objects.filter(email=email).first()
            if user and not user.check_password(senha):
                raise ValidationError("Email ou senha incorretos.")
        return cleaned_data
    
class ClienteUpdateForm(forms.ModelForm):
    
    email = forms.EmailField(required=True) 

    class Meta:
        model = Cliente
        # Inclua apenas os campos que você quer permitir que o cliente edite
        fields = ['nome', 'sobrenome', 'email', 'telefone'] 
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sobrenome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Torna o email não editável
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
        }

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['Profissional', 'servico', 'data_hora'] 
        
    def clean(self):
        cleaned_data = super().clean()
        
        #Obtem dados do formulário
        profissional = cleaned_data.get('Profissional')
        servico = cleaned_data.get('servico')
        data_hora_inicio = cleaned_data.get('data_hora')
        
        # Se algum campo essencial não foi preenchido (erro de campo obrigatório), 
        # a validação de conflito deve ser ignorada para evitar exceptions
        if not all([profissional, servico, data_hora_inicio]):
            return cleaned_data 
        
        #Calcular o tempo de término do NOVO agendamento
        try:
            # Obtém a duração do Servico
            duracao = servico.duracao_minutos 
        except AttributeError:
            raise forms.ValidationError("Erro interno: O Serviço selecionado não possui o campo 'duracao_minutos'.")
            
        data_hora_fim_novo = data_hora_inicio + timedelta(minutes=duracao)
                
        # O conflito acontece quando dois intervalos de tempo [A, B] e [C, D] se sobrepõem.
        # Condição de sobreposição: A < D AND C < B
        
        # Aqui: A = Início do Existente; B = Fim do Existente;
        #       C = data_hora_inicio (Novo); D = data_hora_fim_novo (Novo)
        
        #Agendamentos existentes que começam ANTES do novo agendamento TERMINAR.
        conflitos_potenciais = Agendamento.objects.filter(
            Profissional=profissional,
            cancelado=False,
            # (A < D) - O Existente começa antes do Novo terminar
            data_hora__lt=data_hora_fim_novo, 
            
        ).exclude(
            # Exclui o próprio agendamento se for uma edição
            pk=self.instance.pk if self.instance else None 
        )

        #Verifica se o AGENDAMENTO EXISTENTE TERMINA DEPOIS do NOVO COMEÇAR.
        for agendamento_existente in conflitos_potenciais:
            
            # Pega a duração do serviço do agendamento existente
            duracao_existente = agendamento_existente.servico.duracao_minutos
            data_hora_fim_existente = agendamento_existente.data_hora + timedelta(minutes=duracao_existente)
            
            # (C < B) - O Novo começa antes do Existente terminar.
            # Se as duas condições (Filtro 1 e Filtro 2) forem verdadeiras, há sobreposição.
            if data_hora_inicio < data_hora_fim_existente:
                
                inicio_local = timezone.localtime(agendamento_existente.data_hora) 
                fim_local = timezone.localtime(data_hora_fim_existente)
                
                # Conflito encontrado!
                raise forms.ValidationError(
                    f"Conflito de horário! O profissional {profissional} estará ocupado das "
                    # Usa o objeto datetime convertido para formatar a hora
                    f"{inicio_local.strftime('%H:%M')} às "
                    f"{fim_local.strftime('%H:%M')}."
                )
                        
        return cleaned_data

class ProfissionalForm(forms.ModelForm):

    nome = forms.CharField(label='Nome', max_length=25)
    sobrenome = forms.CharField(label='Sobrenome', max_length=25)
    email = forms.EmailField(label='Email', max_length=100)
    telefone = forms.CharField(label='Telefone', max_length=15)

    class Meta:
        model = Profissional
        fields = [] 
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['nome'].initial = self.instance.user.nome
            self.fields['sobrenome'].initial = self.instance.user.sobrenome
            self.fields['email'].initial = self.instance.user.email
            self.fields['telefone'].initial = self.instance.user.telefone
    
    def save(self, commit=True):
        profissional = super().save(commit=False)
        user = profissional.user
        user.nome = self.cleaned_data['nome']
        user.sobrenome = self.cleaned_data['sobrenome']
        user.email = self.cleaned_data['email']
        user.telefone = self.cleaned_data['telefone']
       
        if commit:
            user.save()
            profissional.save()
        return profissional

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone_limpo = re.sub(r'\D', '', telefone)
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise forms.ValidationError("O número de telefone deve ter 10 ou 11 dígitos, incluindo o DDD.")
                
        return telefone_limpo

class ServicoForm(forms.ModelForm):
    
    tempo = forms.TimeField(
        required=True,
        label='Tempo Estimado (Duração):',
        widget=forms.TimeInput(attrs={
            'type': 'time', 
            'step': '60',   # Passo de 60 segundos (1 minuto)
            'value': '00:30' # Valor padrão de 30 minutos
        })
    )
    
    profissionais = forms.ModelMultipleChoiceField(
        queryset=Profissional.objects.all(),
        required=False,
        label='Designar Funcionário(s):',
        widget=forms.SelectMultiple,
    )

    class Meta:
        model = Servico
        fields = ['nome', 'descricao', 'profissionais'] 
        
        labels = {
            'nome': 'Nome do Serviço:',
            'descricao': 'Descrição:',
        }

    def clean(self):
        cleaned_data = super().clean()
        tempo = cleaned_data.get('tempo')
        
        if tempo and isinstance(tempo, time):
            total_minutos = tempo.hour * 60 + tempo.minute
            
            cleaned_data['duracao_minutos'] = total_minutos
                
        return cleaned_data

class CadastroProfissionalAdminForm(forms.Form):
    nome = forms.CharField(label='Nome', max_length=25)
    sobrenome = forms.CharField(label='Sobrenome', max_length=25)
    email = forms.EmailField(label='Email', max_length=100)
    telefone = forms.CharField(label='Telefone', max_length=15)
    senha = forms.CharField(label='Senha', widget=forms.PasswordInput)
    
    # Validação do E-mail
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if Cliente.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado como cliente ou funcionário.")
        return email

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone_limpo = re.sub(r'\D', '', telefone)
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
             raise ValidationError("O número de telefone deve ter 10 ou 11 dígitos, incluindo o DDD.")
        return telefone_limpo
    
class ProfissionalCadastroForm(forms.Form):
    email = forms.EmailField(required=True)
    nome = forms.CharField(max_length=25, required=True)
    sobrenome = forms.CharField(max_length=25, required=True)
    senha = forms.CharField(widget=forms.PasswordInput, required=True)
    telefone = forms.CharField(max_length=15, required=False) 
    # servicos = forms.ModelMultipleChoiceField(queryset=Servico.objects.all(), required=False)