"""módulo de Visualizações do apps de Riscos """
from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import requer_admin
from .models import PlanoDeRisco

@requer_admin
def painel_riscos(request):
    """lista os planos de risco do usuário logado"""
    planos = PlanoDeRisco.objects.filter(deleted_at__isnull=True).select_related('setor', 'criado_por')
    return render(request, 'riscos/painel_riscos.html', {'planos': planos})

@requer_admin
def detalhe_plano(request, pk):
    """exibe detalhes de um plano de risco"""
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)
    return render(request, 'riscos/detalhe.html', {
        'plano': plano,
        'identificacao': getattr(plano, 'identificacao', None),
        'avaliacao': getattr(plano, 'avaliacao', None),
        'tratamento': getattr(plano, 'tratamento', None),
    })

@requer_admin
def plano_deletar(request, pk):
    """Deletar um plano de risco Soft Delete"""
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)

    if plano.criado_por == request.user or request.user.is_staff:
        if request.method == 'POST':
            plano.soft_delete()
            return redirect('riscos:painel_riscos')
        return render(request, 'riscos/confirmar_exclusao.html', {'objeto': plano})
        
    return redirect('riscos:painel_riscos')
