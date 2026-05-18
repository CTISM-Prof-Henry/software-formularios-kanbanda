from django.contrib import admin
from .models import LogAlteracao


@admin.register(LogAlteracao)
class LogAlteracaoAdmin(admin.ModelAdmin):
    list_display  = ['criado_em', 'model_name', 'objeto_id', 'campo', 'usuario', 'ip']
    list_filter   = ['model_name']
    search_fields = ['model_name', 'descricao', 'usuario__matricula']
    readonly_fields = [f.name for f in LogAlteracao._meta.fields]

    def has_add_permission(self, request):    return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
