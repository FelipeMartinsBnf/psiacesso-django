import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import Http404

from contas.models import Paciente, Psicologo, Usuario
from .forms import *

def roleCadastro(request):
    return render(request, 'cadastro/cadastro_select_role.html', {})

def cadastro(request, tipo_cadastro):

    if request.method == 'POST':
        form_usuario = CustomUserCreationForm(request.POST)
        form_endereco = enderecoForm(request.POST)
        
        if form_usuario.is_valid() and form_endereco.is_valid():
            
            user = form_usuario.save(commit=False)
            if tipo_cadastro == 1:
                user.role = Usuario.Role.PSICOLOGO
            elif tipo_cadastro == 2:
                user.role = Usuario.Role.USUARIO
            else:
                raise Http404("Este tipo de cadastro não está disponível no momento.")
            user.save()
            
            endereco = form_endereco.save(commit=False)
            endereco.usuario = user
            endereco.save()
            
            login(request, user, backend='contas.backends.EmailBackend') 
            return redirect('/') 
    else:
        form_usuario = CustomUserCreationForm()
        form_endereco = enderecoForm()
    
    return render(request, 'auth/cadastro.html', {'user_form': form_usuario, 'address_form': form_endereco})

@login_required # Garante que o usuário já esteja logado
def checar_perfil(request):
    user = request.user
    try:
        if user.role == 'PSICOLOGO':
            psicologo = Psicologo.objects.get(usuario=user)
            return redirect('psi-dashboard')

        elif user.role == 'USUARIO':
            paciente = Paciente.objects.get(usuario=user)
            return redirect('user-dashboard')

    except Psicologo.DoesNotExist:
        return redirect('cadastro_psicologo')

    except Paciente.DoesNotExist:
        return redirect('cadastro_paciente')

    return redirect('login')


def _gerar_horarios(inicio, fim, duracao):
    """Helper para gerar a lista de horários (ex: 08:00, 08:50, 09:40...)"""
    horarios = []
    hora_atual = datetime.datetime.strptime(inicio, '%H:%M')
    hora_fim = datetime.datetime.strptime(fim, '%H:%M')
    delta = datetime.timedelta(minutes=duracao)
    
    while hora_atual < hora_fim:
        horarios.append(hora_atual.time())
        hora_atual += delta
    return horarios

@login_required
def cadastro_psicologo(request):
    if request.method == 'POST':
        form = PsicologoProfileForm(request.POST)
        formset = FormacaoFormSet(request.POST, prefix='formacoes')

        if form.is_valid() and formset.is_valid():
            psicologo = form.save(commit=False)
            psicologo.usuario = request.user
            psicologo.save()
            
            formset.instance = psicologo
            formset.save()
            
            return redirect('psi-dashboard')
    else:
        form = PsicologoProfileForm()
        formset = FormacaoFormSet(prefix='formacoes')
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'cadastro/cadastro_psicologo.html', context)


@login_required
def cadastro_paciente(request):
    if request.method == 'POST':
        form = PacienteProfileForm(request.POST)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
            return redirect('user-dashboard') #TODO: alterar aqui para psi-dash
    else:
        form = PacienteProfileForm()
        
    return render(request, 'cadastro/cadastro_paciente.html', {'form': form})



