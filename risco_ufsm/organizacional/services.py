'''Helpers de querySet de unidade e setor'''
from .models import Setor, Unidade


def qs_unidades(usuario):
    if usuario.is_admin:
        return Unidade.objects.all().order_by('nome')
    # Gestor da Unidade vê só as suas
    unid_ids = usuario.usuario_setores.filter(ativo=True).values_list(
        'setor__unidade_id', flat=True
    )
    return Unidade.objects.filter(id__in=unid_ids).order_by('nome')


def qs_setores(usuario, unidade=None):
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