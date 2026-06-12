"""
os services encapsulam a lógica de negócio isolada das views 
evita que as views virem uma salada de frutas gorda e difícil de manter
"""
import logging
import smtplib
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth import get_user_model
from django.utils import timezone
 
from organizacional.models import Setor, UsuarioSetor

from .models import TokenAtivacao, TokenRecuperacaoSenha, LogAcesso, TentativaLogin

# pylint: disable= no-member
# desabilitei o ´sem mebro´ porque o pylint não reconhece os campos do model,
# mas eles existem e funcionam normalmente

logger = logging.getLogger('accounts')
Usuario  = get_user_model()

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

# helper usados nas views

def qs_escopo(usuario):
    '''
    faz uma consulta de todos os objetos Usuários,
    e depois filtra de acordo com o perfil do usuário logado
    - Administradores e gestores de unidade veem todos os usuários
    - Gestores de setor veem apenas usuários vinculados aos setores que gerenciam
    - Demais usuários veem apenas a si mesmos
    '''
    qs = Usuario.objects.all()
    if usuario.is_admin:
        return qs
    if usuario.is_gestor_unidade:
        return qs

    # se o usuário for gestor de setor, ele só pode ver os
    # usuários vinculados aos setores que ele gerencia.
    # Para isso, a função obtém os IDs dos setores ativos vinculados
    # ao usuário e filtra os usuários que têm vínculo ativo com esses setores.
    # O método distinct() é usado para evitar duplicatas caso um usuário esteja
    # vinculado a múltiplos setores gerenciados pelo gestor.

    if usuario.is_gestor_setor:
        set_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        return qs.filter(usuario_setores__setor_id__in=set_ids).distinct()
    return qs.filter(pk=usuario.pk)

# pylint: disable=no-member
def qs_setores(usuario):
    '''
    Dependendo do perfil do usuário, retorna os setores que ele pode gerenciar:
    - Administradores e gestores de unidade podem ver todos os setores ativos
    - Gestores de setor podem ver apenas os setores aos quais estão vinculados ativamente
    '''
    if usuario.is_admin or usuario.is_gestor_unidade:
        #select_related é usado para otimizar consultas, trazendo os dados
        # da unidade relacionada em uma única consulta ao banco de dados.
        return Setor.objects.filter(ativo=True).select_related('unidade')
    if usuario.is_gestor_setor:
        set_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        return Setor.objects.filter(id__in=set_ids, ativo=True).select_related('unidade')
    return Setor.objects.none()

# pylint: disable=no-member
def atualizar_setores_usuario(usuario, setores_selecionados, usuario_logado, setores_gerenciaveis):
    '''
    Atualiza os vínculos entre um usuário e os setores selecionados no formulário de edição.
    Garante que o usuário só possa ser vinculado a setores dentro do escopo do usuário logado.
     - setores_selecionados: lista de objetos Setor selecionados no formulário
     - usuario_logado: objeto Usuario que está realizando a edição
     - setores_gerenciaveis: queryset de Setor que o usuário_logado tem permissão para gerenciar
    '''
    ids_gerenciaveis = set(setores_gerenciaveis.values_list('id', flat=True))
    ids_selecionados = {setor.id for setor in setores_selecionados}
    ids_invalidos = ids_selecionados - ids_gerenciaveis
    if ids_invalidos:
        raise PermissionError('Setor fora do escopo do usuário logado.')

    vinculos_ativos = usuario.usuario_setores.filter(
        ativo=True,
        setor_id__in=ids_gerenciaveis,
    )
    ids_atuais = set(vinculos_ativos.values_list('setor_id', flat=True))

    for vinculo in vinculos_ativos.exclude(setor_id__in=ids_selecionados):
        vinculo.encerrar()

    for setor in setores_selecionados:
        if setor.id not in ids_atuais:
            UsuarioSetor.objects.create(
                usuario=usuario,
                setor=setor,
                ativo=True,
                criado_por=usuario_logado,
            )