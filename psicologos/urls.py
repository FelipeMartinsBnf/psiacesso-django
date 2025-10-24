from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('psicologo/dashboard/', dashboard, name='psi-dashboard')
]