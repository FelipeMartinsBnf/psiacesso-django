from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from contas.models import Psicologo

@login_required
def dashboard(request):
    #Logica para carregar 4 psicologos mais novos
    recentes = Psicologo.objects.order_by('-id')[:4]
    context = {
        'psicologos': recentes
    }
    return render(request, 'dashboard.html', context)

#Carrega todos os psicologos disponiveis
@login_required
def view_all_psicologs(request):
    psicologos = Psicologo.objects.all()
    context = {
        'psicologos': psicologos
    }
    return render(request, 'psicologos_list.html', context)

