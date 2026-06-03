"""Configuração do app de estrutura organizacional (unidades e setores)."""
from django.apps import AppConfig

class OrganizacionalConfig(AppConfig):
    """Configuração padrão do app organizacional."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'organizacional'
    verbose_name = 'Estrutura Organizacional'
