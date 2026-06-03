"""Configuração WSGI do projeto risco_ufsm."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'risco_ufsm.settings')
application = get_wsgi_application()
