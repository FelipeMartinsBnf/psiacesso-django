from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from contas.models import Especialidade, Psicologo
from psiacesso_main.models import Formacao

@login_required
def dashboard(request):
    #Logica para carregar 4 psicologos mais novos
    recentes = Psicologo.objects.order_by('-id')[:4]
    
    #Carregar as consultas do paciente logado (futuro)
    return render(request, 'dashboard.html', {'psicologos': recentes })

#Carrega todos os psicologos disponiveis
@login_required
def view_all_psicologs(request):
    query = request.GET.get('query', '')
    
    if query:
        psicologos = Psicologo.objects.filter(usuario__first_name__icontains=query).distinct()
    else:
        psicologos = Psicologo.objects.filter()
    return render(request, 'psicologos_list.html', {'psicologos': psicologos, 'query': query})

#Carrega as informações de um psicologo para o paciente
@login_required
def view_detail_psi(request, id):
    psi = Psicologo.objects.get(id=id)
    formacoes = Formacao.objects.filter(psicologo=psi)
    return render(request, 'detalhes_psi.html', {'psi': psi, 'formacoes': formacoes })

#Mostra datas disponíveis para agendamento e outras infos.
@login_required
def view_detail_psi(request, id):
    psi = Psicologo.objects.get(id=id)
    formacoes = Formacao.objects.filter(psicologo=psi)
    return render(request, 'detalhes_psi.html', {'psi': psi, 'formacoes': formacoes })

