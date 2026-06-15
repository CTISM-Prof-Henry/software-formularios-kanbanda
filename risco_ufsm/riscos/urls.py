'''URLS dos riscos'''

from django.urls import path
from . import views

app_name = 'riscos'

urlpatterns = [
    path('',                          views.lista_planos,     name='lista_planos'),
    path('novo/',                     views.novo_plano,       name='novo_plano'),
    path('<int:pk>/',                 views.visualizar_plano, name='visualizar_plano'),
    path('<int:pk>/pdf/',             views.gerar_pdf,        name='gerar_pdf'),
    path('<int:pk>/editar/',          views.editar_plano,     name='editar_plano'),
    path('<int:pk>/excluir/',         views.excluir_plano,    name='excluir_plano'),
    path('<int:pk>/remanejar/',       views.remanejar_plano,  name='remanejar_plano'),
    path('notificacoes/',             views.lista_notificacoes, name='lista_notificacoes'),
    path('admin/painel/',             views.painel_riscos,    name='painel_riscos'),
    path('admin/<int:pk>/detalhe/',   views.detalhe_plano,    name='detalhe_plano'),
    path('admin/<int:pk>/deletar/',   views.plano_deletar,    name='plano_deletar'),
]
