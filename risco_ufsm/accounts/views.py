import logging
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from .decorators import requer_pode_criar_usuario, requer_pode_gerenciar_usuarios, requer_admin
from .forms import (
    LoginForm, RecuperarSenhaForm, RedefinirSenhaForm, AtivacaoContaForm,
    CadastroUsuarioForm, EditarUsuarioForm, MeuPerfilForm, AlterarSenhaForm,
)
from .models import TokenAtivacao, TokenRecuperacaoSenha, LogAcesso, Perfil
from .services import (
    criar_token_ativacao, criar_token_recuperacao,
    enviar_email_ativacao, enviar_email_recuperacao,
    registrar_login_ok, registrar_login_falha,
    registrar_logout, registrar_ativacao, registrar_recuperacao, get_ip,
)
from organizacional.models import Setor, UsuarioSetor

logger   = logging.getLogger('accounts')
Usuario  = get_user_model()


# Login ─────────────────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def view_login(request):
    if request.user.is_authenticated:
        return redirect('painel')
    motivo = request.GET.get('motivo')
    if motivo == 'sessao_expirada':
        messages.warning(request, 'Sessão expirada por inatividade. Faça login novamente.')
    form = LoginForm(request.POST or None)
    erro = None
    if request.method == 'POST' and form.is_valid():
        ident = form.cleaned_data['identificador'].strip()
        senha = form.cleaned_data['senha']
        ip    = get_ip(request)
        ua    = request.META.get('HTTP_USER_AGENT', '')
        user  = auth.authenticate(request, username=ident, password=senha)
        if user:
            auth.login(request, user)
            user.ultimo_login_ip = ip
            user.save(update_fields=['ultimo_login_ip', 'last_login'])
            registrar_login_ok(user, ip, ua)
            return redirect(request.GET.get('next', 'painel'))
        bloqueado = registrar_login_falha(ident, ip, ua)
        if bloqueado:
            erro = 'IP bloqueado temporariamente após múltiplas tentativas. Aguarde 15 minutos.'
        else:
            try:
                u = Usuario.objects.get(email__iexact=ident) if '@' in ident \
                    else Usuario.objects.get(matricula__iexact=ident)
                if not u.conta_ativada:
                    erro = 'Conta não ativada. Verifique seu e-mail institucional.'
                elif not u.ativo:
                    erro = 'Conta desativada. Contate o administrador.'
                else:
                    erro = 'Matrícula/e-mail ou senha incorretos.'
            except Usuario.DoesNotExist:
                erro = 'Matrícula/e-mail ou senha incorretos.'
    return render(request, 'accounts/login.html', {'form': form, 'erro': erro})


# Logout ────────────────────────────────────────────────────────────────────
@login_required
def view_logout(request):
    registrar_logout(request.user, get_ip(request), request.META.get('HTTP_USER_AGENT', ''))
    auth.logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('login')


# Recuperar senha ───────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def view_recuperar_senha(request):
    if request.user.is_authenticated:
        return redirect('painel')
    form    = RecuperarSenhaForm(request.POST or None)
    enviado = False
    if request.method == 'POST' and form.is_valid():
        ident = form.cleaned_data['identificador'].strip()
        ip    = get_ip(request)
        try:
            u = Usuario.objects.get(email__iexact=ident, ativo=True) if '@' in ident \
                else Usuario.objects.get(matricula__iexact=ident, ativo=True)
            if u.conta_ativada:
                t = criar_token_recuperacao(u, ip=ip)
                enviar_email_recuperacao(u, t)
                registrar_recuperacao(u, ip)
        except Usuario.DoesNotExist:
            pass  # resposta genérica — não revela se usuário existe
        enviado = True
    return render(request, 'accounts/recuperar_senha.html', {'form': form, 'enviado': enviado})


# Redefinir senha ───────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def view_redefinir_senha(request, token_uuid):
    try:
        token = TokenRecuperacaoSenha.objects.select_related('usuario').get(token=token_uuid)
    except (TokenRecuperacaoSenha.DoesNotExist, ValueError):
        return render(request, 'accounts/token_invalido.html',
                      {'titulo': 'Link inválido', 'mensagem': 'Link inválido ou já utilizado.'})
    if not token.esta_valido():
        return render(request, 'accounts/token_invalido.html',
                      {'titulo': 'Link expirado', 'mensagem': 'Link expirado. Solicite um novo.',
                       'mostrar_recuperar': True})
    form = RedefinirSenhaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ip = get_ip(request)
        with transaction.atomic():
            token.usuario.set_password(form.cleaned_data['nova_senha'])
            token.usuario.save(update_fields=['password'])
            token.marcar_usado(ip=ip)
            registrar_recuperacao(token.usuario, ip)
        messages.success(request, 'Senha redefinida. Faça login.')
        return redirect('login')
    return render(request, 'accounts/redefinir_senha.html', {'form': form, 'token': token})


# Ativar conta ──────────────────────────────────────────────────────────────
@require_http_methods(['GET', 'POST'])
def view_ativar_conta(request, token_uuid):
    try:
        token = TokenAtivacao.objects.select_related('usuario').get(token=token_uuid)
    except (TokenAtivacao.DoesNotExist, ValueError):
        return render(request, 'accounts/token_invalido.html',
                      {'titulo': 'Link inválido', 'mensagem': 'Link inválido ou já utilizado.'})
    if not token.esta_valido():
        return render(request, 'accounts/token_invalido.html',
                      {'titulo': 'Link expirado',
                       'mensagem': f'Link expirado em {token.expira_em:%d/%m/%Y %H:%M}. Solicite novo ao administrador.'})
    form = AtivacaoContaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ip = get_ip(request)
        with transaction.atomic():
            u = token.usuario
            u.set_password(form.cleaned_data['nova_senha'])
            u.conta_ativada = True
            u.save(update_fields=['password', 'conta_ativada'])
            token.marcar_usado(ip=ip)
            registrar_ativacao(u, ip)
        messages.success(request, f'Conta ativada! Bem-vindo(a), {token.usuario.primeiro_nome}. Faça login.')
        return redirect('login')
    return render(request, 'accounts/ativar_conta.html',
                  {'form': form, 'token': token, 'usuario': token.usuario})


# Painel ────────────────────────────────────────────────────────────────────
@login_required
def view_painel(request):
    u   = request.user
    ctx = {'usuario': u, 'setores': u.get_setores_ativos(), 'unidades': u.get_unidades_ativas()}
    if u.pode_gerenciar_usuarios:
        qs = _qs_escopo(u)
        ctx.update({
            'total_usuarios':    qs.count(),
            'total_inativos':    qs.filter(ativo=False).count(),
            'total_nao_ativ':    qs.filter(conta_ativada=False, ativo=True).count(),
        })
    return render(request, 'accounts/painel.html', ctx)


# Lista de usuários ─────────────────────────────────────────────────────────
@requer_pode_gerenciar_usuarios
def view_lista_usuarios(request):
    u  = request.user
    qs = _qs_escopo(u)

    busca  = request.GET.get('q', '').strip()
    perfil = request.GET.get('perfil', '')
    status = request.GET.get('status', '')

    if busca:
        qs = qs.filter(
            Q(primeiro_nome__icontains=busca) | Q(sobrenome__icontains=busca) |
            Q(matricula__icontains=busca)     | Q(email__icontains=busca) |
            Q(cargo__icontains=busca)
        )
    if perfil:
        qs = qs.filter(perfil=perfil)
    if status == 'ativo':
        qs = qs.filter(ativo=True)
    elif status == 'inativo':
        qs = qs.filter(ativo=False)
    elif status == 'nao_ativado':
        qs = qs.filter(conta_ativada=False, ativo=True)

    return render(request, 'accounts/lista_usuarios.html', {
        'usuarios': qs.select_related('criado_por')
                      .prefetch_related('usuario_setores__setor__unidade'),
        'total': qs.count(),
        'perfis': Perfil.choices,
        'busca': busca, 'filtro_perfil': perfil, 'filtro_status': status,
    })


# Cadastrar usuário ─────────────────────────────────────────────────────────
@requer_pode_criar_usuario
def view_cadastro_usuario(request):
    u          = request.user
    setores_qs = _qs_setores(u)
    form = CadastroUsuarioForm(
        request.POST or None, request.FILES or None,
        usuario_logado=u, queryset_setores=setores_qs,
    )
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            novo = form.save(commit=False)
            novo.criado_por = u
            novo.conta_ativada = False
            novo.set_unusable_password()
            novo.save()
            for setor in form.cleaned_data.get('setores', []):
                UsuarioSetor.objects.create(usuario=novo, setor=setor, ativo=True, criado_por=u)
            token   = criar_token_ativacao(novo)
            enviado = enviar_email_ativacao(novo, token, request)
        if enviado:
            messages.success(request, f'Usuário criado. E-mail enviado para {novo.email}.')
        else:
            messages.warning(request,
                f'Usuário criado, mas e-mail falhou. Link manual: /ativar-conta/{token.token}/')
        return redirect('lista_usuarios')
    return render(request, 'accounts/cadastro_usuario.html',
                  {'form': form, 'titulo': 'Cadastrar Novo Usuário'})


# Editar usuário ────────────────────────────────────────────────────────────
@requer_pode_gerenciar_usuarios
def view_editar_usuario(request, pk):
    u    = request.user
    alvo = get_object_or_404(Usuario, pk=pk)
    if not u.is_admin and not u.pode_editar_usuario(alvo):
        messages.error(request, 'Sem permissão para editar este usuário.')
        return redirect('lista_usuarios')
    form = EditarUsuarioForm(
        request.POST or None, request.FILES or None,
        instance=alvo, usuario_logado=u,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Usuário {alvo.get_nome_completo()} atualizado.')
        return redirect('lista_usuarios')
    return render(request, 'accounts/editar_usuario.html', {
        'form': form, 'alvo': alvo,
        'setores': alvo.get_setores_ativos(),
        'titulo': f'Editar: {alvo.get_nome_completo()}',
    })


# Reenviar ativação ─────────────────────────────────────────────────────────
@requer_pode_criar_usuario
def view_reenviar_ativacao(request, pk):
    alvo    = get_object_or_404(Usuario, pk=pk, conta_ativada=False)
    token   = criar_token_ativacao(alvo)
    enviado = enviar_email_ativacao(alvo, token, request)
    if enviado:
        messages.success(request, f'E-mail reenviado para {alvo.email}.')
    else:
        messages.warning(request, f'Falha no e-mail. Link: /ativar-conta/{token.token}/')
    return redirect('lista_usuarios')


# Ativar/Desativar ──────────────────────────────────────────────────────────
@requer_pode_criar_usuario
@require_http_methods(['POST'])
def view_toggle_ativo(request, pk):
    u    = request.user
    alvo = get_object_or_404(Usuario, pk=pk)
    if alvo == u:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('lista_usuarios')
    if not u.is_admin and alvo.perfil == Perfil.ADMIN:
        messages.error(request, 'Sem permissão para alterar Administradores.')
        return redirect('lista_usuarios')
    alvo.ativo = not alvo.ativo
    alvo.save(update_fields=['ativo', 'atualizado_em'])
    messages.success(request, f'Usuário {"ativado" if alvo.ativo else "desativado"}.')
    return redirect('lista_usuarios')


# Meu perfil ────────────────────────────────────────────────────────────────
@login_required
def view_meu_perfil(request):
    u           = request.user
    form_perfil = MeuPerfilForm(request.POST or None, request.FILES or None, instance=u, prefix='perfil')
    form_senha  = AlterarSenhaForm(request.POST or None, usuario=u, prefix='senha')
    if request.method == 'POST':
        acao = request.POST.get('acao')
        if acao == 'perfil' and form_perfil.is_valid():
            form_perfil.save()
            messages.success(request, 'Dados atualizados.')
            return redirect('meu_perfil')
        if acao == 'senha' and form_senha.is_valid():
            u.set_password(form_senha.cleaned_data['nova_senha'])
            u.save(update_fields=['password'])
            auth.update_session_auth_hash(request, u)
            messages.success(request, 'Senha alterada.')
            return redirect('meu_perfil')
    return render(request, 'accounts/meu_perfil.html', {
        'usuario': u, 'form_perfil': form_perfil,
        'form_senha': form_senha, 'setores': u.get_setores_ativos(),
    })


# Logs de acesso ────────────────────────────────────────────────────────────
@requer_admin
def view_logs_acesso(request):
    qs   = LogAcesso.objects.select_related('usuario').order_by('-criado_em')
    tipo = request.GET.get('tipo', '')
    if tipo:
        qs = qs.filter(tipo=tipo)
    return render(request, 'accounts/logs_acesso.html', {
        'logs': qs[:500], 'tipos': LogAcesso.TIPO_CHOICES, 'filtro_tipo': tipo,
    })


# Helpers ───────────────────────────────────────────────────────────────────
def _qs_escopo(usuario):
    qs = Usuario.objects.all()
    if usuario.is_admin:
        return qs
    if usuario.is_gestor_unidade:
        unid_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor__unidade_id', flat=True)
        set_ids  = Setor.objects.filter(unidade_id__in=unid_ids).values_list('id', flat=True)
        return qs.filter(usuario_setores__setor_id__in=set_ids).distinct()
    if usuario.is_gestor_setor:
        set_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        return qs.filter(usuario_setores__setor_id__in=set_ids).distinct()
    return qs.filter(pk=usuario.pk)


def _qs_setores(usuario):
    if usuario.is_admin:
        return Setor.objects.filter(ativo=True).select_related('unidade')
    if usuario.is_gestor_unidade:
        unid_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor__unidade_id', flat=True)
        return Setor.objects.filter(unidade_id__in=unid_ids, ativo=True).select_related('unidade')
    return Setor.objects.none()
