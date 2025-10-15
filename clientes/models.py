# clientes/models.py (CORRIGIDO)
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password # Não precisa mais disso no save()

# Um Manager para criar usuários e superusuários
class ClienteManager(BaseUserManager):
    def create_user(self, email, senha=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(senha) # Usa o método set_password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, senha=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, senha, **extra_fields)

class Cliente(AbstractBaseUser, PermissionsMixin):

    nome = models.CharField(max_length=25)
    sobrenome = models.CharField(max_length=25)
    email = models.EmailField(unique=True) 
    telefone = models.CharField(max_length=15, null=False)
    # Campo senha ja tem no AbstractBaseUser !
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = ClienteManager()

    # Campos de autenticação
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'sobrenome'] # Campos que serão pedidos ao criar superusuário

    def get_full_name(self):
        return f"{self.nome} {self.sobrenome}"

    def get_short_name(self):
        return self.nome

    def __str__(self)-> str:
        return f"{self.nome} {self.sobrenome} - {self.email}"