# ES-projeto
Usando a tecnologia Django

Passo a passo para que funcione sem problemas na maquina
Instale as seguintes informaçoes

Antes de tudo verifique se o python esta instaldo

no CMD digite o comando
python --vesion

crie um ambiente virtual na sua maquina
evita conflito de versão

No CMD rode

python -m venv venv

depois ative o ambiente virtual

Windows
venv\Scripit\activate

MAC/LINUX

source venv/bin/activate

instale o django

pip install django

para confirmar

django-admin --version

biblioteca que vai precisar para rodar o projeto

pip install django-allauth

pip install django-cors-headers

pip install python-dateutil

#Para realizaçoes dos testes

pip install pytest pytest-django

use 
pytest

caso nao funcionar use o comando

terminal powershell: "$env:DJANGO_SETTINGS_MODULE="agenda.settings"; pytest" e o pytest funciona com esse comando "na minha maquina foi a unica forma que eu consegui rodar o pytest"