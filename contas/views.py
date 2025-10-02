from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

def cadastro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Salva o novo usuário no banco de dados
            login(request, user) # Loga o usuário automaticamente após o cadastro
            return redirect('/') # Redireciona para a página inicial
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'templates/auth/cadastro.html', {'form': form})
