from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    #Logica para carregar 4 psicologos mais novos
    recentes = Psicologo.objects.order_by('-id')[:4]
    return render(request, 'dashboard.html', {'psicologos': recentes })
