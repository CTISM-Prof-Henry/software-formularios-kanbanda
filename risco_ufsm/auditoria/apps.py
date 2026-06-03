"""Configuração da aplicação de auditoria e histórico de alterações."""
from django.apps import AppConfig

class AuditoriaConfig(AppConfig):
    """Configuração da aplicação de auditoria e histórico."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditoria'
    verbose_name = 'Auditoria e Histórico'
