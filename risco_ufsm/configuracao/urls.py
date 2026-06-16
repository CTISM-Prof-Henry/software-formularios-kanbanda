from django.urls import path
from . import views

app_name = 'configuracao'

urlpatterns = [
    path('', views.painel_configuracao, name='painel_configuracao'),
    
    #desafiopdi
    path('desafio/novo/', views.desafio_criar, name='desafio_criar'),
    path('desafio/<int:pk>/editar/', views.desafio_editar, name='desafio_editar'),
    path('desafio/<int:pk>/deletar/', views.desafio_deletar, name='desafio_deletar'),
    
    # objetivopdi
    path('objetivo/novo/', views.objetivo_criar, name='objetivo_criar'),
    path('objetivo/<int:pk>/editar/', views.objetivo_editar, name='objetivo_editar'),
    path('objetivo/<int:pk>/deletar/', views.objetivo_deletar, name='objetivo_deletar'),
    
    # macroprocesso
    path('macroprocesso/novo/', views.macroprocesso_criar, name='macroprocesso_criar'),
    path('macroprocesso/<int:pk>/editar/', views.macroprocesso_editar, name='macroprocesso_editar'),
    path('macroprocesso/<int:pk>/deletar/', views.macroprocesso_deletar, name='macroprocesso_deletar'),
]