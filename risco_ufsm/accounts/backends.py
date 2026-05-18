import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

logger = logging.getLogger('accounts')
Usuario = get_user_model()


class MatriculaEmailBackend(ModelBackend):
    """
    Backend de autenticação que aceita matrícula OU e-mail institucional.
    Verifica se a conta está ativa e ativada antes de autenticar.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        # Tenta por e-mail primeiro, depois por matrícula
        try:
            if '@' in str(username):
                usuario = Usuario.objects.get(email__iexact=username.strip())
            else:
                usuario = Usuario.objects.get(matricula__iexact=username.strip())
        except Usuario.DoesNotExist:
            # Executa hash dummy para prevenir timing attacks
            Usuario().set_password(password)
            logger.debug('Autenticação falhou — identificador não encontrado: %s', username)
            return None
        except Usuario.MultipleObjectsReturned:
            logger.error('Múltiplos usuários para o identificador: %s', username)
            return None

        # Verifica senha
        if not usuario.check_password(password):
            logger.debug('Autenticação falhou — senha incorreta: %s', usuario.matricula)
            return None

        # Verifica conta ativa
        if not usuario.ativo:
            logger.info('Autenticação bloqueada — usuário inativo: %s', usuario.matricula)
            return None

        # Verifica ativação da conta
        if not usuario.conta_ativada:
            logger.info('Autenticação bloqueada — conta não ativada: %s', usuario.matricula)
            return None

        return usuario

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
