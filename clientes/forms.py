from django.core.exceptions import ValidationError
import re
from django import forms
from .models import Cliente  # Importando o modelo Cliente

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

    # **PASSO CRÍTICO 4: Sobrescrever save() para HASHING**
    def save(self, commit=True):
        user = super().save(commit=False)
        senha_plana = self.cleaned_data["senha"]
        user.set_password(senha_plana) # HASHING AQUI!
        if commit:
            user.save()
        return user
# ---------------------------------------------


    
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