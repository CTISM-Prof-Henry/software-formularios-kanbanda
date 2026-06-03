"""Configuração principal de URLs do projeto risco_ufsm."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('organizacional.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customiza o admin
admin.site.site_header = 'RiskShield | UFSM — Administração'
admin.site.site_title  = 'RiskShield | UFSM'
admin.site.index_title = 'Painel Administrativo'
