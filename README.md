Atividade padão de projeto
padrões q eu estou ultilizando nesse projeto são:

Padão criacional o Factory Method Padão estrutual o Adapter tambem conhecido como Wrapper Padão comportamental o Template Method Cada um dos padroes estao comentado em como eu ultilizei na funcionalidade que implementei e tbm ultilizei para me basear nos padroes o site refactoring guri e o arquivo que foi implementado os padroes eh no "models.py"

Factory Method

Eh um padrão que se comporta como uma fabrica literalmente tendo uma classe "master" e dentro dela tendo outras classes "menores" que no final se tornam um unico objeto.. Como na minnha aplicação a minha classe "master" eh o ClienteManager q atua como fabrica O produto abstrato, o usuario do Django(AbstractBaseUser) e o BaseUserManager definem a interface para a criaçao do usuario a fabrica(ClienteManager) herda de BaseUserManager e interpleta os metodos de criação Metodos da "fabrica": create_user(self, email, password=none, **extra_fields) ele eh o principal factory method, ele encapsula as etapas necessarias para criação de um cliente, valida o email, normaliza, hash da senha(user.set_password), e salva no BD create_superuser(com os mesmos atributos de create_user) eh uma variaçao do metodo em vez de duplicar a logica de criação de usuario, ele apenas define as flags especificas para um super usuario no caso um ADMINISTRADOR(is_staff=True, is_superuser=True) e, em seguida, reusa o create_user para concluir a criação

Adapter

O adapter permite q interfaces incompativeis trabalhem juntas ele atua como um Wtapper que traduz a interface de uma classe(adaptado) para outra interface que o codigo cliente espera.

Na minha aplicaçao eu uso o Adapter de duas maneiras que saem fora do padrão esperado pela interface Django na primeira eh adptando o gerenciador de objetos, o Django ORM espera que o atributo objects em um modelo de usuario seja uma instancia da BaseUserManager, adaptado a minha classe ClienteManager(factory) eh o objeto personalizado o adaptador eh na linha "objects = ClienteManager() na classe Cliente tornando o ClienteManager o manipulador do BD padrão, adaptando a interface que o django ORM espera.. A segunda adptação eh na interface de usuario o meu modelo Cliente eh personalisado com os campos "email, nome, telefone" as constantes de classes e metodos em "Cliente" atuam como adapter: USERNAME_FIELD = "email" adapta o campo email para ser o campo que o django usa para login, REQUIRED_FIELDS = ['nome', 'sobrenome'] adapta os campos de nome para serem os campos obrigatorios na criação do super usuario.

Template method

Ele define o esqueleto de um algoritmo em um metodo, deixando as subclasses definam os passos especificos os "ganchos" do algoritmo na minha aplicação Cliente e AbstractBaseUser o template method na classe AbstractBaseUser da qual o Cliente herda, define o algoritmo completo de autentificação e gerenciamento de permissoes o esqueleto ja esta pronto, ja os ganchos o AbstractBaseUser exije que as subclasse do Cliente implementem certos "ganchos" para completar o algoritimo, USERNAME_FIELD eh um gancho para definir qual campo será o nome de usuário defini como 'email', REQUIRED_FIELDS eh outro gancho para você definir quais campos são necessários na criação como ['nome', 'sobrenome'], metodos como get_full_name() e get_short_name() são ganchos exigidos para a renderização do usuário no Admin ou em outras partes, permitindo que defina como o nome completo/abreviado deve ser composto.

referencias: https://refactoring.guru/pt-br/design-patterns/factory-method https://refactoring.guru/pt-br/design-patterns/adapter https://refactoring.guru/pt-br/design-patterns/template-method

Usando a tecnologia Django
Passo a passo para que funcione sem problemas na maquina Instale as seguintes informaçoes

Antes de tudo verifique se o python esta instaldo

no CMD digite o comando python --vesion

crie um ambiente virtual na sua maquina evita conflito de versão

No CMD rode

python -m venv venv

depois ative o ambiente virtual

Windows venv\Scripit\activate

MAC/LINUX

source venv/bin/activate

instale o django

pip install django

para confirmar

django-admin --version

biblioteca que vai precisar para rodar o projeto

pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

pip install django-allauth

pip install django-cors-headers

pip install python-dateutil

#Para realizaçoes dos testes

pip install pytest pytest-django

use pytest

caso nao funcionar use o comando

terminal powershell: "$env:DJANGO_SETTINGS_MODULE="agenda.settings"; pytest" e o pytest funciona com esse comando "na minha maquina foi a unica forma que eu consegui rodar o pytest"