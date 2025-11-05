from django.contrib import admin
from django.urls import path
from .views import dashboard, gerenciar_disponibilidade_grid

urlpatterns = [
    path('psicologo/dashboard', dashboard, name='psi-dashboard'),
    path('psicologo/disponibilidade', gerenciar_disponibilidade_grid, name='disponibilidade'),
]