from django.contrib import admin
from django.urls import path
from .views import cancelar_consulta_psi, consulta_detalhe_psi, dashboard, gerenciar_disponibilidade_grid, salvar_anotacao_consulta, perfil_psicologo_view, editar_perfil_psicologo

urlpatterns = [
    path('psicologo/dashboard', dashboard, name='psi-dashboard'),
    path('psicologo/disponibilidade', gerenciar_disponibilidade_grid, name='disponibilidade'),
    path('psicologo/cancelar/<int:consulta_id>', cancelar_consulta_psi, name='cancelar_consulta_psi'),
    path('psicologo/sessao/anotacao/<int:consulta_id>', salvar_anotacao_consulta, name='save_anotacao_consulta'),

    #Modals
    path('psicologo/consulta/detalhe/<int:consulta_id>', consulta_detalhe_psi, name='consulta_detalhe_psi'),

    path('psicologo/perfil/<int:id>/', perfil_psicologo_view, name='perfil-psi'),

    path('psicologo/editar/', editar_perfil_psicologo, name='editar_perfil')
]