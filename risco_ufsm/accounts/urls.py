from django.urls import path
from . import views

urlpatterns = [
    # Autenticação pública
    path('login/',                                    views.view_login,            name='login'),
    path('logout/',                                   views.view_logout,           name='logout'),
    path('recuperar-senha/',                          views.view_recuperar_senha,  name='recuperar_senha'),
    path('redefinir-senha/<uuid:token_uuid>/',        views.view_redefinir_senha,  name='redefinir_senha'),
    path('ativar-conta/<uuid:token_uuid>/',           views.view_ativar_conta,     name='ativar_conta'),

    # Painel e perfil (autenticado)
    path('painel/',                                   views.view_painel,           name='painel'),
    path('meu-perfil/',                               views.view_meu_perfil,       name='meu_perfil'),

    # Gestão de usuários (restrito por perfil)
    path('usuarios/',                                 views.view_lista_usuarios,   name='lista_usuarios'),
    path('usuarios/novo/',                            views.view_cadastro_usuario, name='cadastro_usuario'),
    path('usuarios/<int:pk>/editar/',                 views.view_editar_usuario,   name='editar_usuario'),
    path('usuarios/<int:pk>/toggle-ativo/',           views.view_toggle_ativo,     name='toggle_ativo'),
    path('usuarios/<int:pk>/reenviar-ativacao/',      views.view_reenviar_ativacao, name='reenviar_ativacao'),

    # Logs (apenas admin)
    path('logs/acesso/',                              views.view_logs_acesso,      name='logs_acesso'),

    # Rota raiz
    path('', lambda req: __import__('django.shortcuts', fromlist=['redirect']).redirect('login'), name='home'),
]
