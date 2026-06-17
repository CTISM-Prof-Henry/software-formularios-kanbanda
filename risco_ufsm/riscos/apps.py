'''App de riscos'''

from django.apps import AppConfig

class RiscosConfig(AppConfig):
    '''configuração do app'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'riscos'
    verbose_name = 'Alteração de Risco'

    def ready(self):
        '''Registra os models relacionados à alteração de planos de risco.'''
        signals_module = 'risco.signals'
        try:
            __import__(signals_module)
        except ImportError:
            pass