from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Unidade, Setor, UsuarioSetor


@admin.register(Unidade)
class UnidadeAdmin(SimpleHistoryAdmin):
    list_display  = ['nome', 'sigla', 'tipo', 'ativo']
    list_filter   = ['tipo', 'ativo']
    search_fields = ['nome', 'sigla']


@admin.register(Setor)
class SetorAdmin(SimpleHistoryAdmin):
    list_display  = ['nome', 'unidade', 'ativo']
    list_filter   = ['unidade', 'ativo']
    search_fields = ['nome', 'unidade__nome']


@admin.register(UsuarioSetor)
class UsuarioSetorAdmin(SimpleHistoryAdmin):
    list_display  = ['usuario', 'setor', 'data_inicio', 'data_fim', 'ativo', 'criado_por']
    list_filter   = ['ativo', 'setor__unidade']
    search_fields = ['usuario__matricula', 'usuario__primeiro_nome', 'setor__nome']
    readonly_fields = ['criado_em', 'history']

    def has_delete_permission(self, request, obj=None):
        return False   # nunca deletar fisicamente
