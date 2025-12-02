from django.urls import path
from .views import dashboard, view_all_psicologs, view_detail_psi, agendar, get_horarios_disponiveis, agenda_paciente_view, consulta_detalhe_paciente, cancelar_consulta_paciente, perfil_paciente, editar_perfil_paciente 

urlpatterns = [
    path('paciente/dashboard/', dashboard, name='user-dashboard'),
    path('paciente/psicologos', view_all_psicologs, name='user-psi-list'),
    path('paciente/psicologos/<int:id>', view_detail_psi, name='user-psi-detail'),
    path('paciente/psicologos/agendar/<int:psicologo_id>', agendar, name='agendar_consulta'),
    path('paciente/agenda', agenda_paciente_view, name='agenda_paciente'),
    path('paciente/cancelar/<int:consulta_id>', cancelar_consulta_paciente, name='cancelar_consulta'),

    path('paciente/perfil/<int:pk>/', perfil_paciente, name='perfil-paciente'),

    #Modals

    path('paciente/consulta/detalhe/<int:consulta_id>', consulta_detalhe_paciente, name='consulta_detalhe_paciente'),
    
    path('api/horarios/<int:psicologo_id>/', get_horarios_disponiveis, name='get_horarios_disponiveis'),

    path('paciente/perfil/editar/', editar_perfil_paciente, name='editar_perfil_paciente'), 
]
    
    