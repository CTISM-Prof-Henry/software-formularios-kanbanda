'''helpers para as views de riscos, retornando os planos por
permissão de usuário e se eles podem editar ou não'''

from .models import PlanoDeRisco

def qs_planos(usuario):
    """Retorna os planos de risco que o usuário tem permissão de ver."""
    base = PlanoDeRisco.objects.filter(deleted_at__isnull=True).select_related(
        'setor__unidade', 'criado_por', 'identificacao', 'avaliacao', 'tratamento'
    )
    if usuario.is_admin:
        return base
    if usuario.is_gestor_unidade:
        unidade_ids = usuario.get_unidades_ativas().values_list('id', flat=True)
        return base.filter(setor__unidade_id__in=unidade_ids)
    # Gestor de Setor e Servidor: apenas o próprio setor
    setor_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
    return base.filter(setor_id__in=setor_ids)

def pode_editar(self, usuario):
    '''retorna os planos que usuário tem permissão para editar'''
    if usuario.is_admin:
        return True
    if usuario.is_gestor_unidade:
        unidade_ids = usuario.get_unidades_ativas().values_list('id', flat=True)
        return self.setor.unidade_id in list(unidade_ids)
    if usuario.is_gestor_setor:
        setor_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        return self.setor_id in list(setor_ids)
    return False
