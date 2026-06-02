'''Configuração da aplicação de contas e autenticação,
incluindo o registro dos models relacionados à autenticação e segurança.'''
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    '''Configuração da aplicação de contas e autenticação.'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Autenticação e Usuários'

    def ready(self):
        '''Registra os models relacionados à autenticação e segurança dos usuários.'''
        signals_module = 'accounts.signals'
        try:
            __import__(signals_module)
        except ImportError:
            pass
