"""
Decoradores são funções especiais que envolvem outras funções (normalmente views) para adicionar funcionalidades extras, como controle de acesso, verificação de perfil, etc.
Eles são usados para garantir que apenas usuários com os perfis adequados possam acessar determinadas views, e para verificar se a conta do usuário está ativada antes de permitir o acesso
"""
import functools
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from .models import Perfil
 

def _acesso_negado(request, mensagem='Você não tem permissão para acessar esta página.'):
    return render(request, 'acesso_negado.html', {'mensagem': mensagem}, status=403)


def requer_perfil(*perfis):
    """Exige que o usuário tenha um dos perfis listados."""
    def decorator(view_func):
        @login_required
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.perfil not in perfis:
                return _acesso_negado(request)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def requer_admin(view_func):
    """Apenas Administrador do Sistema."""
    return requer_perfil(Perfil.ADMIN)(view_func)


def requer_pode_criar_usuario(view_func):
    """Admin e Gestor da Unidade podem criar usuários."""
    return requer_perfil(Perfil.ADMIN, Perfil.GESTOR_UNIDADE)(view_func)


def requer_pode_gerenciar_usuarios(view_func):
    """Admin, Gestor Unidade e Gestor Setor podem listar/gerenciar usuários."""
    return requer_perfil(Perfil.ADMIN, Perfil.GESTOR_UNIDADE, Perfil.GESTOR_SETOR)(view_func)


def requer_conta_ativada(view_func):
    """Garante que o usuário ativou a conta."""
    @login_required
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.conta_ativada:
            return _acesso_negado(request, 'Sua conta ainda não foi ativada.')
        return view_func(request, *args, **kwargs)
    return wrapper
