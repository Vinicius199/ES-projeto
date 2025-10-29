from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password 

# PADRÃO DE CRIAÇÃO: FACTORY METHOD (FÁBRICA)
# ====================================================================
# O ClienteManager atua como a Fábrica. Ele encapsula a lógica de criação 
# e inicialização de objetos Cliente e Superuser, garantindo que o objeto 
# retornado esteja sempre configurado corretamente (com senha hasheada).
class ClienteManager(BaseUserManager):
    # FACTORY METHOD: create_user
    # Responsável por criar e retornar objetos Clientes válidos.
    def create_user(self, email, senha=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(senha)
        # Salva o objeto Cliente no banco de dados (retorna o objeto pronto)
        user.save(using=self._db)
        return user
    
    # create_superuser
    # Variação da Fábrica que define configurações específicas (is_staff, is_superuser).
    def create_superuser(self, email, senha=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # is_active: Garante que o usuário pode logar
        extra_fields.setdefault('is_active', True) 
        
        # Validações de segurança (Opcional, mas boas práticas)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        # Agora o create_user recebe todas as flags e salva 
        return self.create_user(email, senha, **extra_fields)

# ====================================================================
# PADRÃO ESTRUTURAL: ADAPTER (ADAPTADOR)
# PADRÃO COMPORTAMENTAL: TEMPLATE METHOD (MÉTODO MODELO)
# ====================================================================
# Cliente herda de AbstractBaseUser e implementa os "ganchos" exigidos
# pelo Template Method do Django, atuando como um Adaptador para o ORM.
class Cliente(AbstractBaseUser, PermissionsMixin):

    nome = models.CharField(max_length=25)
    sobrenome = models.CharField(max_length=25)
    email = models.EmailField(unique=True) 
    telefone = models.CharField(max_length=15, null=False)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # ADAPTER: O ClienteManager (Fábrica) é adaptado para ser o 'objects' padrão 
    # que o ORM do Django espera para criar e buscar instâncias de Cliente.
    objects = ClienteManager() 

    # IMPLEMENTAÇÃO DO TEMPLATE METHOD ( EXIGIDOS PELO ABSTRACTBASEUSER)
    
    # ADAPTER / TEMPLATE : Adaptação do Campo de Login.
    # O Template Method (AbstractBaseUser) define que deve haver um campo de login.
    # Esta linha ADAPTA o 'email' para ser o campo que o Template usará para autenticação.
    USERNAME_FIELD = 'email'
    
    # TEMPLATE : Campos Obrigatórios para a Etapa de Criação.
    # O Template Method (AbstractBaseUser) exige esta lista para criação de superusuário.
    REQUIRED_FIELDS = ['nome', 'sobrenome'] 

    # ADAPTER / TEMPLATE : Adaptação e Implementação dos Métodos de Nome.
    # O Template Method (e o Admin do Django) espera que o modelo implemente esses métodos
    # para exibir o nome. Você ADAPTA os campos 'nome' e 'sobrenome' para essa interface.
    def get_full_name(self):
        return f"{self.nome} {self.sobrenome}"

    def get_short_name(self):
        return self.nome

    def __str__(self)-> str:
        return f"{self.nome} {self.sobrenome} - {self.email}"

class Profissional(models.Model):
    # Relaciona o profissional ao usuário Cliente (opcional, mas bom para login/gestão)
    # Você pode querer usar o modelo Cliente para login, mas se for um profissional externo, use campos normais.
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15, blank=True)
    
    # 💡 RELACIONAMENTO MANY-TO-MANY COM SERVIÇO
    # Um profissional pode fazer vários serviços e um serviço pode ter vários profissionais.
    servicos = models.ManyToManyField('Servico', related_name='profissionais_aptos') 
    
    # Se você quiser que o profissional tenha uma ligação com o modelo Cliente, descomente esta linha:
    # usuario_cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, null=True, blank=True)


    def get_full_name(self):
        return f"{self.nome} {self.sobrenome}"

    def __str__(self):
        return self.get_full_name()

class Servico(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField()
    duracao_minutos = models.PositiveIntegerField(default=60)

    def __str__(self):
        return self.nome

# tabela Agendamentos
class Agendamento(models.Model):
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        related_name='agendamentos'
    )
    
    servico = models.ForeignKey(
        Servico, 
        on_delete=models.PROTECT
    )
    
    Profissional =models.ForeignKey(
        'Profissional',
        on_delete=models.PROTECT,
        related_name='agendamentos_realizados',
        verbose_name='Profissional Agendado'
    )

    confirmado = models.BooleanField(
        default=False, # Definir como False é o padrão, mas a view vai sobrescrever.
        verbose_name='Agendamento Confirmado'
    )

    cancelado = models.BooleanField(
        default=False, 
        verbose_name='Cancelado'
    )

    data_hora = models.DateTimeField()
    
    class Meta:
        ordering = ['data_hora']
    
    def __str__(self):
        return f"Agendamento de {self.servico} para {self.cliente} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"