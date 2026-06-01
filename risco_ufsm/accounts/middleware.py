"""
Os middlewares funcionam como uma espécie de pedágio para as requisições
todas as requisições passam por eles antes de chegar às views
"""
import logging
from django.conf import settings
from django.contrib import auth
from django.shortcuts import redirect
from django.utils import timezone
from django.urls import reverse

logger = logging.getLogger('accounts')

# Rotas que não precisam de proteção de sessão
_ROTAS_PUBLICAS = frozenset([
    '/login/', '/recuperar-senha/', '/redefinir-senha/',
    '/ativar-conta/', '/static/', '/media/',
])


def _e_rota_publica(path):
    for prefixo in _ROTAS_PUBLICAS:
        if path.startswith(prefixo):
            return True
    return False


class SessaoExpiradaMiddleware:
    """
    Expira a sessão do usuário após SESSION_COOKIE_AGE segundos de inatividade.
    Registra o evento no log de acesso.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.tempo_limite = getattr(settings, 'SESSION_COOKIE_AGE', 1800)

    def __call__(self, request):
        if request.user.is_authenticated and not _e_rota_publica(request.path):
            ultima_atividade = request.session.get('_ultima_atividade')
            agora = timezone.now().timestamp()

            if ultima_atividade:
                inativo_por = agora - ultima_atividade
                if inativo_por > self.tempo_limite:
                    logger.info(
                        'Sessão expirada por inatividade: usuário %s, IP %s',
                        request.user.matricula, _get_ip(request),
                    )
                    _registrar_log_expiracao(request)
                    auth.logout(request)
                    return redirect(
                        f"{reverse('login')}?motivo=sessao_expirada"
                    )

            request.session['_ultima_atividade'] = agora

        return self.get_response(request)


class BruteForceMiddleware:
    """
    Monitora tentativas de login. Bloqueia o IP após N tentativas falhas.
    A lógica de contagem está nas views; este middleware apenas bloqueia
    IPs já marcados antes mesmo de chegar à view de login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == reverse('login') and request.method == 'POST':
            ip = _get_ip(request)
            from accounts.models import TentativaLogin
            try:
                tentativa = TentativaLogin.objects.get(ip=ip)
                if tentativa.esta_bloqueado():
                    from django.http import HttpResponseForbidden
                    logger.warning('IP bloqueado tentando login: %s', ip)
                    return HttpResponseForbidden(
                        '<h2>IP temporariamente bloqueado por segurança. '
                        'Aguarde 15 minutos e tente novamente.</h2>'
                    )
            except TentativaLogin.DoesNotExist:
                pass

        return self.get_response(request)


# ── Utilitários ───────────────────────────────────────────────────────────────

def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _registrar_log_expiracao(request):
    try:
        from accounts.models import LogAcesso
        LogAcesso.objects.create(
            tipo=LogAcesso.TIPO_SESSAO_EXP,
            usuario=request.user if request.user.is_authenticated else None,
            ip=_get_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
    except Exception as exc:
        logger.error('Erro ao registrar log de expiração: %s', exc)
