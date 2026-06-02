from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from accounts.decorators import requer_pode_criar_usuario, requer_admin
from .models import Unidade, Setor, UsuarioSetor
from .forms import UnidadeForm, SetorForm, VincularUsuarioSetorForm

Usuario = get_user_model()


# Helpers de querySet de unidade e setor ─────────────────────────────────────────────────────────

def _qs_unidades(usuario):
    if usuario.is_admin:
        return Unidade.objects.all().order_by('nome')
    # Gestor da Unidade vê só as suas
    unid_ids = usuario.usuario_setores.filter(ativo=True).values_list(
        'setor__unidade_id', flat=True
    )
    return Unidade.objects.filter(id__in=unid_ids).order_by('nome')


def _qs_setores(usuario, unidade=None):
    if usuario.is_admin:
        qs = Setor.objects.select_related('unidade').order_by('unidade__nome', 'nome')
    else:
        unid_ids = usuario.usuario_setores.filter(ativo=True).values_list(
            'setor__unidade_id', flat=True
        )
        qs = Setor.objects.filter(
            unidade_id__in=unid_ids
        ).select_related('unidade').order_by('unidade__nome', 'nome')
    if unidade:
        qs = qs.filter(unidade=unidade)
    return qs



# UNIDADES
@requer_pode_criar_usuario
def lista_unidades(request):
    unidades = _qs_unidades(request.user).prefetch_related('setores')
    return render(request, 'organizacional/lista_unidades.html', {
        'unidades': unidades,
        'total': unidades.count(),
    })


@requer_admin
def nova_unidade(request):
    form = UnidadeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        u = form.save()
        messages.success(request, f'Unidade "{u.nome}" criada com sucesso.')
        return redirect('lista_unidades')
    return render(request, 'organizacional/form_unidade.html', {
        'form': form, 'titulo': 'Nova Unidade', 'acao': 'Criar',
    })


@requer_admin
def editar_unidade(request, pk):
    unidade = get_object_or_404(Unidade, pk=pk)
    form = UnidadeForm(request.POST or None, instance=unidade)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Unidade "{unidade.nome}" atualizada.')
        return redirect('lista_unidades')
    return render(request, 'organizacional/form_unidade.html', {
        'form': form, 'titulo': f'Editar: {unidade.nome}', 'acao': 'Salvar',
        'objeto': unidade,
    })


@requer_admin
@require_http_methods(['POST'])
def toggle_unidade(request, pk):
    unidade = get_object_or_404(Unidade, pk=pk)
    # Não apaga — apenas desativa (soft delete semântico)
    unidade.ativo = not unidade.ativo
    unidade.save(update_fields=['ativo'])
    acao = 'ativada' if unidade.ativo else 'desativada'
    messages.success(request, f'Unidade "{unidade.nome}" {acao}.')
    return redirect('lista_unidades')


# SETORES

@requer_pode_criar_usuario
def lista_setores(request):
    unidade_id = request.GET.get('unidade')
    unidade_sel = None
    if unidade_id:
        unidade_sel = get_object_or_404(Unidade, pk=unidade_id)

    setores  = _qs_setores(request.user, unidade=unidade_sel)
    unidades = _qs_unidades(request.user)

    return render(request, 'organizacional/lista_setores.html', {
        'setores':     setores,
        'total':       setores.count(),
        'unidades':    unidades,
        'unidade_sel': unidade_sel,
    })


@requer_pode_criar_usuario
def novo_setor(request):
    form = SetorForm(request.POST or None, usuario_logado=request.user)
    if request.method == 'POST' and form.is_valid():
        s = form.save()
        messages.success(request, f'Setor "{s.nome}" criado em "{s.unidade}".')
        return redirect('lista_setores')
    return render(request, 'organizacional/form_setor.html', {
        'form': form, 'titulo': 'Novo Setor / Subunidade', 'acao': 'Criar',
    })


@requer_pode_criar_usuario
def editar_setor(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    # Gestor da Unidade só edita setores da sua unidade
    if not request.user.is_admin:
        unid_ids = request.user.usuario_setores.filter(ativo=True).values_list(
            'setor__unidade_id', flat=True
        )
        if setor.unidade_id not in list(unid_ids):
            messages.error(request, 'Sem permissão para editar este setor.')
            return redirect('lista_setores')

    form = SetorForm(request.POST or None, instance=setor, usuario_logado=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Setor "{setor.nome}" atualizado.')
        return redirect('lista_setores')
    return render(request, 'organizacional/form_setor.html', {
        'form': form, 'titulo': f'Editar: {setor.nome}', 'acao': 'Salvar',
        'objeto': setor,
    })


@requer_pode_criar_usuario
@require_http_methods(['POST'])
def toggle_setor(request, pk):
    setor = get_object_or_404(Setor, pk=pk)
    setor.ativo = not setor.ativo
    setor.save(update_fields=['ativo'])
    acao = 'ativado' if setor.ativo else 'desativado'
    messages.success(request, f'Setor "{setor.nome}" {acao}.')
    return redirect('lista_setores')


# VÍNCULOS USUÁRIO - SETOR

@requer_pode_criar_usuario
def vinculos_setor(request, pk):
    """Lista e gerencia os vínculos de um setor específico."""
    setor   = get_object_or_404(Setor, pk=pk)
    ativos  = (UsuarioSetor.objects.filter(setor=setor, ativo=True)
            .select_related('usuario', 'criado_por'))
    hist    = (UsuarioSetor.objects.filter(setor=setor, ativo=False)
            .select_related('usuario').order_by('-data_fim'))

    return render(request, 'organizacional/vinculos_setor.html', {
        'setor':  setor,
        'ativos': ativos,
        'hist':   hist,
    })


@requer_pode_criar_usuario
@require_http_methods(['POST'])
def encerrar_vinculo(request, pk):
    """Encerra (soft delete) um vínculo usuário–setor."""
    vinculo = get_object_or_404(UsuarioSetor, pk=pk, ativo=True)
    vinculo.encerrar()
    messages.success(request, f'Vínculo de {vinculo.usuario.get_nome_completo()} encerrado.')
    return redirect('vinculos_setor', pk=vinculo.setor_id)


@requer_pode_criar_usuario
def adicionar_vinculo(request, setor_pk):
    """Adiciona um novo vínculo usuário–setor."""
    setor = get_object_or_404(Setor, pk=setor_pk)

    # Usuários disponíveis (sem vínculo ativo no setor)
    ja_vinculados = (UsuarioSetor.objects.filter(setor=setor, ativo=True)
                     .values_list('usuario_id', flat=True))
    usuarios_disp = (Usuario.objects.exclude(id__in=ja_vinculados)
                     .filter(ativo=True).order_by('primeiro_nome'))

    if request.method == 'POST':
        usuario_id  = request.POST.get('usuario')
        data_inicio = request.POST.get('data_inicio')
        if not usuario_id:
            messages.error(request, 'Selecione um usuário.')
        else:
            usuario = get_object_or_404(Usuario, pk=usuario_id)
            with transaction.atomic():
                UsuarioSetor.objects.create(
                    usuario=usuario,
                    setor=setor,
                    data_inicio=data_inicio or None,
                    ativo=True,
                    criado_por=request.user,
                )
            messages.success(request, f'{usuario.get_nome_completo()} vinculado a {setor.nome}.')
            return redirect('vinculos_setor', pk=setor.pk)

    return render(request, 'organizacional/adicionar_vinculo.html', {
        'setor':        setor,
        'usuarios_disp': usuarios_disp,
    })
