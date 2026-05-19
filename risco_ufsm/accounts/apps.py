from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Autenticação e Usuários'

    def ready(self):
        import accounts.signals  #NOQA: F401 - Importa os signals para registrar os handlers de login/logout.
