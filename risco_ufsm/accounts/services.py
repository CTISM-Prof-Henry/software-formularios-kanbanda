"""
os services encapsulam a lógica de negócio isolada das views 
evita que as views virem uma salada de frutas gorda e difícil de manter
"""
import logging
import smtplib
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.utils import timezone

from .models import TokenAtivacao, TokenRecuperacaoSenha, LogAcesso, TentativaLogin

# pylint: disable= no-member
# desabilitei o ´sem mebro´ porque o pylint não reconhece os campos do model,
# mas eles existem e funcionam normalmente

logger = logging.getLogger('accounts')

# pylint: disable=no-member
def criar_token_ativacao(usuario):
    """Cria e retorna um novo token de ativação para o usuário."""
    # Invalida tokens anteriores não usados
    TokenAtivacao.objects.filter(usuario=usuario, usado=False).update(
        usado=True, usado_em=timezone.now()
 )
    return TokenAtivacao.objects.create(usuario=usuario)

# pylint: disable=no-member
def criar_token_recuperacao(usuario, ip=None):
    """Cria e retorna um novo token de recuperação de senha."""
    # Invalida tokens anteriores
    TokenRecuperacaoSenha.objects.filter(usuario=usuario, usado=False).update(
        usado=True, usado_em=timezone.now()
    )
    return TokenRecuperacaoSenha.objects.create(usuario=usuario, ip_solicitante=ip)


# E-mails

def enviar_email_ativacao(usuario, token, _request=None):
    """Envia e-mail de ativação de conta com link e token."""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    link = f'{site_url}/ativar-conta/{token.token}/'

    assunto = 'RiskShield — Ative sua conta de acesso'
    mensagem_txt = (
        f'Olá, {usuario.primeiro_nome}!\n\n'
        f'Sua conta no Sistema de Gestão de Riscos da UFSM foi criada.\n\n'
        f'Para ativar sua conta e criar sua senha, acesse o link abaixo:\n'
        f'{link}\n\n'
        f'Este link expira em {getattr(settings, "TOKEN_ATIVACAO_HORAS", 48)} horas.\n\n'
        f'Caso não reconheça este cadastro, ignore este e-mail.\n\n'
        f'Atenciosamente,\nEquipe RiskShield'
    )

    try:
        send_mail(
            subject=assunto,
            message=mensagem_txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            fail_silently=False,
        )
        logger.info('E-mail de ativação enviado para %s', usuario.email)
        return True
    except (BadHeaderError, smtplib.SMTPException, OSError) as exc:
        logger.error('Falha ao enviar e-mail de ativação para %s: %s', usuario.email, exc)
        return False


def enviar_email_recuperacao(usuario, token):
    """Envia e-mail de recuperação de senha."""
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    link = f'{site_url}/redefinir-senha/{token.token}/'
    minutos = getattr(settings, 'TOKEN_RECUPERACAO_MINUTOS', 15)

    assunto = 'RiskShield — Redefinição de senha'
    mensagem_txt = (
        f'Olá, {usuario.primeiro_nome}!\n\n'
        f'Recebemos uma solicitação de redefinição de senha para sua conta.\n\n'
        f'Acesse o link abaixo para criar uma nova senha:\n'
        f'{link}\n\n'
        f'⚠️ Este link expira em {minutos} minutos.\n\n'
        f'Se você não solicitou a redefinição, ignore este e-mail.\n'
        f'Sua senha atual permanece inalterada.\n\n'
        f'Atenciosamente,\nEquipe RiskShield'
    )

    try:
        send_mail(
            subject=assunto,
            message=mensagem_txt,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            fail_silently=False,
        )
        logger.info('E-mail de recuperação enviado para %s', usuario.email)
        return True
    except (BadHeaderError, smtplib.SMTPException, OSError) as exc:
        logger.error('Falha ao enviar e-mail de recuperação para %s: %s', usuario.email, exc)
        return False



# pylint: disable=no-member
def registrar_login_ok(usuario, ip, user_agent=''):
    '''Registra um login bem-sucedido e reseta tentativas falhas do IP.'''
    LogAcesso.objects.create(
        tipo=LogAcesso.TIPO_LOGIN_OK,
        usuario=usuario,
        ip=ip,
        user_agent=user_agent[:500],
    )
    # Reseta tentativas falhas do IP
    TentativaLogin.objects.filter(ip=ip).update(tentativas=0, bloqueado_ate=None)


# pylint: disable=no-member
def registrar_login_falha(identificador, ip, user_agent=''):
    '''Registra uma tentativa de login falha e verifica bloqueio por brute force.'''
    LogAcesso.objects.create(
        tipo=LogAcesso.TIPO_LOGIN_FALHA,
        identificador_tentado=identificador[:200],
        ip=ip,
        user_agent=user_agent[:500],
    )
    # Incrementa contador brute force
    tentativa, _ = TentativaLogin.objects.get_or_create(ip=ip)
    max_t = getattr(settings, 'BRUTE_FORCE_MAX_TENTATIVAS', 5)
    blq_m = getattr(settings, 'BRUTE_FORCE_BLOQUEIO_MINUTOS', 15)
    bloqueado = tentativa.incrementar(max_t, blq_m)
    if bloqueado:
        LogAcesso.objects.create(
            tipo=LogAcesso.TIPO_BLOQUEIO,
            ip=ip,
            detalhes={'tentativas': tentativa.tentativas},
        )
        logger.warning('IP %s bloqueado após %d tentativas falhas', ip, tentativa.tentativas)
    return bloqueado

# pylint: disable=no-member
def registrar_logout(usuario, ip, user_agent=''):
    '''Registra um logout do usuário.'''
    LogAcesso.objects.create(
        tipo=LogAcesso.TIPO_LOGOUT,
        usuario=usuario,
        ip=ip,
        user_agent=user_agent[:500],
    )


# pylint: disable=no-member
def registrar_ativacao(usuario, ip):
    '''Registra a ativação de conta do usuário.'''
    LogAcesso.objects.create(
        tipo=LogAcesso.TIPO_ATIVACAO,
        usuario=usuario,
        ip=ip,
    )

# pylint: disable=no-member
def registrar_recuperacao(usuario, ip):
    '''Registra a recuperação de senha do usuário.'''
    LogAcesso.objects.create(
        tipo=LogAcesso.TIPO_RECUPERACAO,
        usuario=usuario,
        ip=ip,
    )

def get_ip(request):
    '''Obtém o endereço IP do cliente a partir do request, considerando proxies.'''
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')
