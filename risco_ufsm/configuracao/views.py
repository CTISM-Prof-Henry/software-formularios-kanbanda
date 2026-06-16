"""Views e controle de fluxo para o módulo de configuração do PDI e Macroprocessos."""

from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import requer_pode_configurar
from .models import DesafioPDI, ObjetivoPDI, Macroprocesso
from .forms import DesafioPDIForm, ObjetivoPDIForm, MacroprocessoForm


@requer_pode_configurar
def painel_configuracao(request):
    """View principal do painel de configuracao."""
    desafios = DesafioPDI.objects.filter(deleted_at__isnull=True)
    objetivos = ObjetivoPDI.objects.filter(deleted_at__isnull=True)
    macroprocessos = Macroprocesso.objects.filter(deleted_at__isnull=True)

    return render(request, 'configuracao/painel.html', {
        'desafios': desafios,
        'objetivos': objetivos,
        'macroprocessos': macroprocessos,
    })


# CRUD DesafioPDI

@requer_pode_configurar
def desafio_criar(request):
    """View para criar um novo desafio PDI."""
    form = DesafioPDIForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('configuracao:painel_configuracao')
    contexto = {
        'form': form,
        'titulo': 'Criar Desafio PDI',
        'action_label': 'Criar',
        'volta_label': 'Voltar para o Painel',
        'volta_url': 'configuracao:painel_configuracao'
    }
    return render(request, 'configuracao/form.html', contexto)


@requer_pode_configurar
def desafio_editar(request, pk):
    """View para editar um desafio PDI existente."""
    desafio = get_object_or_404(DesafioPDI, pk=pk, deleted_at__isnull=True)
    form = DesafioPDIForm(request.POST or None, instance=desafio)
    if form.is_valid():
        form.save()
        return redirect('configuracao:painel_configuracao')

    contexto = {
        'form': form,
        'titulo': 'Editar Desafio PDI',
        'action_label': 'Editar',
        'volta_label': 'Voltar para o Painel',
        'volta_url':'configuracao:painel_configuracao' 
    }
    
    return render(request, 'configuracao/form.html', contexto)

@requer_pode_configurar
def desafio_deletar(request, pk):
    """View para deletar um desafio PDI."""
    desafio = get_object_or_404(DesafioPDI, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        desafio.soft_delete()
        return redirect('configuracao:painel_configuracao')
    return render(
        request,
        'configuracao/confirmar_exclusao.html',
        {'objeto': desafio, 'tipo': 'Desafio PDI'}
    )


# CRUD ObjetivoPDI

@requer_pode_configurar
def objetivo_criar(request):
    """View para criar um novo objetivo PDI."""
    form = ObjetivoPDIForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('configuracao:painel_configuracao')
    contexto = {
        'form': form,
        'titulo': 'Criar Objetivo PDI',
        'action_label': 'Criar',
        'volta_label': 'Voltar para o Painel',
        'volta_url': 'configuracao:painel_configuracao'
    }
    return render(request, 'configuracao/form.html', contexto)


@requer_pode_configurar
def objetivo_editar(request, pk):
    """View para editar um objetivo PDI existente."""
    objetivo = get_object_or_404(ObjetivoPDI, pk=pk, deleted_at__isnull=True)
    form = ObjetivoPDIForm(request.POST or None, instance=objetivo)
    if form.is_valid():
        form.save()
        return redirect('configuracao:painel_configuracao')
    contexto = {
        'form': form,
        'titulo': 'Editar Objetivo PDI',
        'action_label': 'Editar',
        'volta_label': 'Voltar para o Painel',
        'volta_url': 'configuracao:painel_configuracao'
    }
    return render(request, 'configuracao/form.html', contexto)

@requer_pode_configurar
def objetivo_deletar(request, pk):
    """View para deletar um objetivo PDI."""
    objetivo = get_object_or_404(ObjetivoPDI, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        objetivo.soft_delete()
        return redirect('configuracao:painel_configuracao')
    return render(
        request,
        'configuracao/confirmar_exclusao.html',
        {'objeto': objetivo, 'tipo': 'Objetivo PDI'}
    )


# CRUD Macroprocesso

@requer_pode_configurar
def macroprocesso_criar(request):
    """View para criar um novo macroprocesso."""
    form = MacroprocessoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('configuracao:painel_configuracao')
    contexto = {
        'form': form,
        'titulo': 'Criar Macroprocesso',
        'action_label': 'Criar',
        'volta_label': 'Voltar para o Painel',
        'volta_url': 'configuracao:painel_configuracao'
    }
    return render(request, 'configuracao/form.html', contexto)


@requer_pode_configurar
def macroprocesso_editar(request, pk):
    """View para editar um macroprocesso existente."""
    macro = get_object_or_404(Macroprocesso, pk=pk, deleted_at__isnull=True)
    form = MacroprocessoForm(request.POST or None, instance=macro)
    if form.is_valid():
        form.save()
        return redirect('configuracao:painel_configuracao')
    contexto = {
        'form': form,
        'titulo': 'Editar Macroprocesso',
        'action_label': 'Editar',
        'volta_label': 'Voltar para o Painel',
        'volta_url': 'configuracao:painel_configuracao'
    }
    return render(request, 'configuracao/form.html', contexto)


@requer_pode_configurar
def macroprocesso_deletar(request, pk):
    """View para deletar um macroprocesso."""
    macro = get_object_or_404(Macroprocesso, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        macro.soft_delete()
        return redirect('configuracao:painel_configuracao')
    return render(
        request,
        'configuracao/confirmar_exclusao.html',
        {'objeto': macro, 'tipo': 'Macroprocesso'}
    )