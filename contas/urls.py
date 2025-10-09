# core/urls.py

from django.contrib import admin
from django.urls import path
from contas.forms import EmailLoginForm
from contas import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
            template_name='auth/login.html', authentication_form=EmailLoginForm 
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('tipo-cadastro', views.roleCadastro, name='select_tipo_cadastro'),
    path('cadastro/<int:tipo_cadastro>', views.cadastro, name='tipo_cadastro'),

    path('cadastro/psicologo/', views.cadastro_psicologo, name='cadastro_psicologo'),
    path('cadastro/paciente/',  views.cadastro_paciente, name='cadastro_paciente'),
]