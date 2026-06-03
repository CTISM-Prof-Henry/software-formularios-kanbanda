"""Rotas do app organizacional."""

from django.urls import path
from . import views

urlpatterns = [
    # Unidades
    path('unidades/',                    views.lista_unidades,  name='lista_unidades'),
    path('unidades/nova/',               views.nova_unidade,    name='nova_unidade'),
    path('unidades/<int:pk>/editar/',    views.editar_unidade,  name='editar_unidade'),
    path('unidades/<int:pk>/toggle/',    views.toggle_unidade,  name='toggle_unidade'),

    # Setores
    path('setores/',                     views.lista_setores,   name='lista_setores'),
    path('setores/novo/',                views.novo_setor,      name='novo_setor'),
    path('setores/<int:pk>/editar/',     views.editar_setor,    name='editar_setor'),
    path('setores/<int:pk>/toggle/',     views.toggle_setor,    name='toggle_setor'),
    path('setores/<int:pk>/vinculos/',   views.vinculos_setor,  name='vinculos_setor'),
    path('setores/<int:setor_pk>/vinculos/add/', views.adicionar_vinculo, name='adicionar_vinculo'),
    path('vinculos/<int:pk>/encerrar/', views.encerrar_vinculo, name='encerrar_vinculo'),
]
