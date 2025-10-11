from django.core.exceptions import ValidationError
import re
from django import forms
from .models import Cliente  # Importando o modelo Cliente

class CadastroForm(forms.ModelForm):
    class Meta:
        model = Cliente  # Usando o modelo Cliente
        fields = ['nome', 'sobrenome', 'telefone', 'email', 'senha']  # Campos do formulário
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Seu Nome'}),
            'sobrenome': forms.TextInput(attrs={'placeholder': 'Sobrenome'}),
            'telefone': forms.TextInput(attrs={'placeholder': 'Telefone'}),
            'email': forms.EmailInput(attrs={'placeholder': 'E-mail'}),
            'senha': forms.PasswordInput(attrs={'placeholder': 'Senha', type:'password'}),
        }
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')

        # Remove qualquer caractere não numérico
        telefone = re.sub(r'\D', '', telefone)

        # Verifica se o telefone tem 10 ou 11 dígitos
        if len(telefone) < 10 or len(telefone) > 11:
            raise ValidationError("O número de telefone deve ter 10 ou 11 dígitos, incluindo o DDD.")

        # Verifica se o telefone contém apenas números
        if not telefone.isdigit():
            raise ValidationError("O número de telefone deve conter apenas números.")

        # Verifica se o DDD é válido (dois primeiros dígitos devem ser numéricos e entre 11 e 99)
        ddd = telefone[:2]
        if not re.match(r'^[1-9][0-9]$', ddd):
            raise ValidationError("O DDD deve ser válido (exemplo: 11 para São Paulo).")

        return telefone
    
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