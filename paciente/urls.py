from django.contrib import admin
from django.urls import path, re_path 
from contas.views import checar_perfil
from .views import dashboard, view_all_psicologs, view_detail_psi

urlpatterns = [
    path('paciente/dashboard/', dashboard, name='user-dashboard'),
    path('paciente/psicologos/', view_all_psicologs, name='user-psi-list'),
    path('paciente/psicologos/<int:id>', view_detail_psi, name='user-psi-detail'),
    path('paciente/psicologos/agendar/<int:id>', view_detail_psi, name='agendar_consulta')
]
    
    