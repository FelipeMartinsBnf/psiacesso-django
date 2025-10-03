# core/urls.py

from django.contrib import admin
from django.urls import path, re_path 
from contas.views import checar_perfil
from .views import dashboard

urlpatterns = [
    
    path('dashboard/', dashboard, name='dashboard'),
    
    # Rota raiz do site: redireciona para a nossa lógica de verificação
    # Se o usuário acessar "meusite.com/", ele cairá aqui.
    path('', checar_perfil, name='root'),

    # ROTA PEGA-TUDO: Deve ser a ÚLTIMA da lista.
    # Qualquer URL que não combinou com as de cima, cairá aqui.
    re_path(r'^.*$', checar_perfil, name='catch_all')
]