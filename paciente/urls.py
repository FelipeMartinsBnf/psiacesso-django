from django.urls import path
from .views import dashboard, view_all_psicologs, view_detail_psi, agendar, get_horarios_disponiveis

urlpatterns = [
    path('paciente/dashboard/', dashboard, name='user-dashboard'),
    path('paciente/psicologos', view_all_psicologs, name='user-psi-list'),
    path('paciente/psicologos/<int:id>', view_detail_psi, name='user-psi-detail'),
    path('paciente/psicologos/agendar/<int:psicologo_id>', agendar, name='agendar_consulta'),
    
    
    path('api/horarios/<int:psicologo_id>/', get_horarios_disponiveis, name='get_horarios_disponiveis'),
]
    
    