from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from contas.models import Paciente, Psicologo
from .forms import CustomUserCreationForm, PacienteProfileForm, PsicologoProfileForm

def cadastro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            login(request, user, backend='contas.backends.EmailBackend') 
            return redirect('/') 
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/cadastro.html', {'form': form})

@login_required # Garante que o usuário já esteja logado
def checar_perfil(request):
    user = request.user

    try:
        if user.role == 'PSICOLOGO':
            psicologo = Psicologo.objects.get(usuario=user)
            return redirect('dashboard')

        elif user.role == 'USUARIO':
            paciente = Paciente.objects.get(usuario=user)
            return redirect('dashboard')

    except Psicologo.DoesNotExist:
        return redirect('cadastro_psicologo')

    except Paciente.DoesNotExist:
        return redirect('cadastro_paciente')

    return redirect('login')


@login_required
def cadastro_psicologo(request):
    # O padrão para processar formulários no Django
    if request.method == 'POST':
        # Cria uma instância do formulário com os dados enviados
        form = PsicologoProfileForm(request.POST)
        if form.is_valid():
            # Cria o objeto do modelo, mas não salva no banco ainda (commit=False)
            perfil = form.save(commit=False)
            # Associa o perfil ao usuário que está logado
            perfil.usuario = request.user
            # Agora sim, salva no banco de dados
            perfil.save()
            # Redireciona para o dashboard após o sucesso
            return redirect('dashboard')
    else:
        # Se não for POST, apenas cria um formulário em branco
        form = PsicologoProfileForm()
        
    return render(request, 'perfis/cadastro_psicologo.html', {'form': form})

@login_required
def cadastro_paciente(request):
    if request.method == 'POST':
        form = PacienteProfileForm(request.POST)
        if form.is_valid():
            perfil = form.save(commit=False)
            perfil.usuario = request.user
            perfil.save()
            return redirect('dashboard')
    else:
        form = PacienteProfileForm()
        
    return render(request, 'perfis/cadastro_paciente.html', {'form': form})



