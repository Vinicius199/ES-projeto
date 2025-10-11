from django.db import models
from django.contrib.auth.hashers import make_password

class Cliente(models.Model):
    nome = models.CharField(max_length=25)
    sobrenome = models.CharField(max_length=25)
    email = models.EmailField(unique=True, primary_key=True)
    telefone = models.CharField(max_length=15, null=False)
    senha = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        #fazendo hash da senha antes de salvar
        if self.senha:
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)
        
    def __str__(self)-> str:
        return f"{self.nome} {self.sobrenome} - {self.email}"