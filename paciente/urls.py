from django.contrib import admin
from django.urls import path, re_path 
from contas.views import checar_perfil
from .views import dashboard, view_all_psicologs

urlpatterns = [
    path('paciente/dashboard/', dashboard, name='user-dashboard'),
    path('paciente/psicologos-disponiveis/', view_all_psicologs, name='user-psi-list')
]
    
    