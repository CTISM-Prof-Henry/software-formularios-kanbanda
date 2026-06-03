# Guia de Instalação e Execução
Siga as instruções utilizando o **PowerShell** para rodar o projeto localmente.

```powershell
# Entrar na pasta do código
cd .\<seulocal>\software-formularios-kanbanda-main\software-formularios-kanbanda-main\risco_ufsm

# Criar e ativar o ambiente virtual
python3 -m venv venv
Set-ExecutionPolicy Unrestricted -Scope Process
. venv/Scripts/Activate.ps1

# Instalar dependências
python -m pip install -r requirements.txt

# Migrations
python manage.py migrate

# Criar primeiro administrador
python manage.py criar_admin_inicial

# Rodar
python manage.py runserver 

``` 