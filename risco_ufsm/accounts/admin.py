from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from simple_history.admin import SimpleHistoryAdmin

from .models import Usuario, TokenAtivacao, TokenRecuperacaoSenha, LogAcesso, TentativaLogin, Perfil


@admin.register(Usuario)
class UsuarioAdmin(SimpleHistoryAdmin, UserAdmin):
    list_display  = ['matricula', 'get_nome_completo', 'email', 'perfil', 'ativo', 'conta_ativada', 'criado_em']
    list_filter   = ['perfil', 'ativo', 'conta_ativada']
    search_fields = ['matricula', 'email', 'primeiro_nome', 'sobrenome']
    ordering      = ['primeiro_nome']
    readonly_fields = ['criado_em', 'atualizado_em', 'deleted_at', 'ultimo_login_ip', 'last_login']

    fieldsets = (
        ('Identificação', {'fields': ('matricula', 'email', 'primeiro_nome', 'sobrenome', 'foto', 'telefone', 'cargo')}),
        ('Perfil e Acesso', {'fields': ('perfil', 'ativo', 'conta_ativada', 'is_staff', 'is_superuser')}),
        ('Rastreabilidade', {'fields': ('criado_por', 'criado_em', 'atualizado_em', 'deleted_at', 'ultimo_login_ip', 'last_login')}),
        ('Permissões Django', {'fields': ('groups', 'user_permissions'), 'classes': ('collapse',)}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': (
            'matricula', 'email', 'primeiro_nome', 'sobrenome',
            'perfil', 'password1', 'password2',
        )}),
    )

    def get_queryset(self, request):
        return self.model.objects.todos()


@admin.register(TokenAtivacao)
class TokenAtivacaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'criado_em', 'expira_em', 'usado']
    list_filter  = ['usado']
    readonly_fields = ['token', 'criado_em', 'usado_em', 'ip_ativacao']


@admin.register(TokenRecuperacaoSenha)
class TokenRecuperacaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'criado_em', 'expira_em', 'usado']
    list_filter  = ['usado']
    readonly_fields = ['token', 'criado_em', 'usado_em']


@admin.register(LogAcesso)
class LogAcessoAdmin(admin.ModelAdmin):
    list_display  = ['tipo', 'usuario', 'identificador_tentado', 'ip', 'criado_em']
    list_filter   = ['tipo']
    search_fields = ['ip', 'identificador_tentado', 'usuario__matricula']
    readonly_fields = list('tipo usuario identificador_tentado ip user_agent detalhes criado_em'.split())

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TentativaLogin)
class TentativaLoginAdmin(admin.ModelAdmin):
    list_display = ['ip', 'tentativas', 'bloqueado_ate', 'ultima_tentativa']
    readonly_fields = ['ultima_tentativa']
