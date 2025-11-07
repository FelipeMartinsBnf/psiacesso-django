import datetime
from contas.models import Psicologo
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from psiacesso_main.models import DisponibilidadePsicologo
from .forms import AgendaGridForm # Importe o novo form

@login_required
def dashboard(request):
    #Logica para carregar 4 psicologos mais novos
    return render(request, 'dashboard-psi.html', {})

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
def gerenciar_disponibilidade_grid(request):
    try:
        psicologo = request.user.psicologo
    except Psicologo.DoesNotExist:
        messages.error(request, "Perfil de psicólogo não encontrado.")
        return redirect('root')

    # Duração da consulta e horários da grade
    duracao = psicologo.duracao_minutos
    # Você pode tornar '07:00' e '22:00' configuráveis depois
    horarios_grade = _gerar_horarios('07:00', '22:00', duracao)
    dias_semana = DisponibilidadePsicologo.DIAS_CHOICES

    if request.method == 'POST':
        form = AgendaGridForm(request.POST)
        if form.is_valid():
            horarios_selecionados = form.cleaned_data['horarios_selecionados']
            
            # --- Lógica de Sincronização ---
            # 1. Apague todas as disponibilidades antigas deste psicólogo
            DisponibilidadePsicologo.objects.filter(psicologo=psicologo).delete()
            
            # 2. Crie as novas com base no que foi selecionado
            novas_disponibilidades = []
            for item in horarios_selecionados:
                novas_disponibilidades.append(
                    DisponibilidadePsicologo(
                        psicologo=psicologo,
                        dia_semana=int(item['dia']),
                        hora_inicio=datetime.time.fromisoformat(item['hora'])
                    )
                )
            
            # 3. Salve tudo no banco de uma vez (mais eficiente)
            DisponibilidadePsicologo.objects.bulk_create(novas_disponibilidades)
            
            messages.success(request, "Agenda atualizada com sucesso!")
            return redirect('psi-dashboard')
    else:
        form = AgendaGridForm()

    # --- Lógica para o GET ---
    disponibilidades_salvas = DisponibilidadePsicologo.objects.filter(psicologo=psicologo)
    # Busca as disponibilidades já salvas para pré-selecionar a grade
    # Cria um conjunto (Set) de STRINGS no formato "DIA,HORA"
    # Ex: {"1,09:00:00", "1,09:50:00", "3,14:00:00"}
    horarios_selecionados_set = {
        f"{d.dia_semana},{d.hora_inicio.isoformat()}" for d in disponibilidades_salvas
    }
    
    # Cria um conjunto (Set) para busca rápida no template
    # Ex: {(1, '09:00:00'), (3, '14:00:00')}
    horarios_selecionados_set = {
            f"{d.dia_semana},{d.hora_inicio.strftime('%H:%M:%S')}" for d in disponibilidades_salvas
        }
    print("DEBUG DA VIEW (horarios_selecionados_set):", horarios_selecionados_set)
    context = {
        'form': form,
        'dias_semana': dias_semana,
        'horarios_grade': horarios_grade,
        'horarios_selecionados_set': horarios_selecionados_set,
    }
    return render(request, 'disponibilidade.html', context)
