import datetime
from contas.models import Paciente, Psicologo
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from psiacesso_main.models import AnotacaoPsicologo, Consulta, DisponibilidadePsicologo
from .forms import AgendaGridForm, AnotacaoForm
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

@login_required
def dashboard(request):
    try:
        # 1. Identificar o paciente logado
        psi = request.user.psicologo
    except Psicologo.DoesNotExist:
        messages.error(request, "Perfil de paciente não encontrado.")
        return redirect('psi-dashboard')

    # 2. Calcular a semana que queremos exibir
    try:
        # Tenta pegar uma data da URL (para navegação)
        target_date_str = request.GET.get('dia', None)
        target_date = datetime.date.fromisoformat(target_date_str)
    except (ValueError, TypeError):
        # Se não houver, usa a data de hoje
        target_date = datetime.date.today()

    # Encontra a Segunda-feira (início da semana)
    start_of_week = target_date - datetime.timedelta(days=target_date.weekday())
    # Encontra o Domingo (fim da semana)
    end_of_week = start_of_week + datetime.timedelta(days=6)

    # 3. Preparar os dados para o cabeçalho do template
    dias_da_semana = []
    for i in range(7):
        dias_da_semana.append(start_of_week + datetime.timedelta(days=i))

    # 4. Definir os limites da nossa grade de horário (ex: 7h às 19h)
    GRID_START_HOUR = 7
    GRID_END_HOUR = 19
    # Total de minutos que a grade visível representa
    total_grid_minutes = (GRID_END_HOUR - GRID_START_HOUR) * 60

    # 5. Buscar as consultas do paciente para esta semana
    consultas = Consulta.objects.filter(
        psicologo=psi,
        paciente__ativo=True,
        data_horario__date__range=(start_of_week, end_of_week),
        status='confirmado'
    ).select_related('psicologo', 'psicologo__usuario') # Otimiza a busca

    # 6. Processar as consultas para o template
    consultas_processadas = []
    for consulta in consultas:
        try:
            duracao = consulta.psicologo.duracao_minutos
        except AttributeError:
            duracao = 50 # Valor padrão se o campo não existir

        start_time = consulta.data_horario.time()
        start_minutes = (start_time.hour * 60) + start_time.minute
        
        # Minutos desde o início da grade (ex: 7h)
        grid_start_minutes = GRID_START_HOUR * 60
        minutes_from_top = start_minutes - grid_start_minutes

        # Calcula a posição e altura em porcentagem
        top_percent = (minutes_from_top / total_grid_minutes) * 100
        height_percent = (duracao / total_grid_minutes) * 100
        
        # Garante que o card não comece antes ou termine depois da grade
        if top_percent < 0: top_percent = 0
        if (top_percent + height_percent) > 100:
            height_percent = 100 - top_percent

        consultas_processadas.append({
            'consulta': consulta,
            'dia_index': consulta.data_horario.weekday(), # 0=Seg, 1=Ter...
            'top': top_percent,
            'height': height_percent,
        })

    # 7. Links de navegação
    nav_prev = start_of_week - datetime.timedelta(days=7)
    nav_next = start_of_week + datetime.timedelta(days=7)

    context = {
        'dias_da_semana': dias_da_semana,
        'consultas_processadas': consultas_processadas,
        'grid_horas_labels': range(GRID_START_HOUR, GRID_END_HOUR), # Rótulos (7, 8, 9...)
        'nav_prev_dia': nav_prev.isoformat(),
        'nav_next_dia': nav_next.isoformat(),
        'semana_display': f"{start_of_week.strftime('%d de %b')} - {end_of_week.strftime('%d de %b')}"
    }

    return render(request, 'dashboard-psi.html', context)

@login_required
def consulta_detalhe_psi(request, consulta_id):
    """
    Busca os detalhes de uma consulta para carregar no modal.
    Esta view retorna APENAS o HTML parcial.
    """
    try:
        psi = request.user.psicologo
    except Psicologo.DoesNotExist:
        return HttpResponse("Acesso não autorizado.", status=403)

    # Garante que a consulta existe E pertence ao psicólogo logado
    consulta = get_object_or_404(
        Consulta,
        pk=consulta_id,
        psicologo=psi
    )
    
    # Renderiza o template parcial que vamos criar
    return render(request, 'partials/_modal_consulta_psi.html', {
        'consulta': consulta
    })

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
    # Você pode tornar '07:00' e '18:00' configuráveis depois
    horarios_grade = _gerar_horarios('07:00', '19:00', duracao)
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


@login_required
def cancelar_consulta_psi(request, consulta_id):
    """
    Permite que o paciente cancele uma consulta.
    Redireciona de volta para a agenda do paciente.
    """
    try:
        psicologo = request.user.psicologo
    except Psicologo.DoesNotExist:
        messages.error(request, "Acesso não autorizado.")
        return redirect('psi-dashboard')

    consulta = get_object_or_404(
        Consulta,
        pk=consulta_id,
        psicologo=psicologo
    )

    # Apenas permite cancelar se a consulta ainda não ocorreu
    if consulta.data_horario > timezone.now():
        consulta.status = 'cancelado'
        consulta.save()
        messages.success(request, "Consulta cancelada com sucesso.")
    else:
        messages.error(request, "Não é possível cancelar consultas passadas.")

    return redirect('psi-dashboard')

@login_required
def salvar_anotacao_consulta(request, consulta_id):
    # Busca a consulta e garante que o psicólogo é o dono dela
    consulta = get_object_or_404(Consulta, pk=consulta_id, psicologo__usuario=request.user)
    
    # Tenta buscar a anotação existente, se houver
    try:
        anotacao = AnotacaoPsicologo.objects.get(consulta=consulta)
    except AnotacaoPsicologo.DoesNotExist:
        anotacao = None

    if request.method == 'POST':
        form = AnotacaoForm(request.POST, instance=anotacao)
        if form.is_valid():
            nova_anotacao = form.save(commit=False)
            nova_anotacao.consulta = consulta
            nova_anotacao.psicologo = consulta.psicologo
            nova_anotacao.data_criacao = timezone.now()
            nova_anotacao.save()
            messages.success(request, "Anotações salvas com sucesso!")
            return redirect('psi-dashboard')  # Ou onde preferir
        else:
            messages.error(request, "Erro ao salvar as anotações. Verifique os dados e tente novamente.")
    else:
        form = AnotacaoForm(instance=anotacao)

    return render(request, 'anotacao_form.html', {
        'form': form,
        'consulta': consulta
    })

