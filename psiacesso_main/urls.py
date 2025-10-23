# core/urls.py

from django.contrib import admin
from django.urls import path, re_path 
from contas.views import checar_perfil

urlpatterns = [
    # Rota raiz do site: redireciona para a nossa lógica de verificação
    # Se o usuário acessar "meusite.com/", ele cairá aqui.
    path('', checar_perfil, name='root')
]