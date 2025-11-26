from django.shortcuts import render
from django.utils.safestring import mark_safe
import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from contas.models import Especialidade, Psicologo
from psiacesso_main.models import Formacao, Paciente, Consulta, DisponibilidadePsicologo
from django.http import HttpResponse, JsonResponse
from .utils import PacienteCalendar # Importe o calendário
from .forms import ConsultaForm
from django.shortcuts import get_object_or_404, render, redirect

@login_required
def dashboard(request):
    #Logica para carregar 4 psicologos mais novos
    recentes = Psicologo.objects.order_by('-id')[:4]
    
    #Pegar as consultas mais recentes    
    consultas = Consulta.objects.filter(paciente=request.user.paciente, status='confirmado').order_by('data_horario')[:5]
    return render(request, 'dashboard.html', {'psicologos': recentes, 'consultas': consultas})

#Carrega todos os psicologos disponiveis
@login_required
def view_all_psicologs(request):
    psicologos = Psicologo.objects.all()
    return render(request, 'psicologos_list.html', {'psicologos': psicologos })

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

# Função para salvar um agendamento
@login_required
def agendar(request, psicologo_id):
    psicologo = get_object_or_404(Psicologo, pk=psicologo_id)
    # Tenta buscar o perfil de Paciente do usuário logado
    try:
        paciente = request.user.paciente # Supondo que você tem o OneToOneField 'paciente' no seu usuário
    except Paciente.DoesNotExist:
        messages.error(request, "Você precisa de um perfil de paciente para agendar.")
        return redirect('root') # Mude para sua home

    # --- LÓGICA DO POST (SALVAR A CONSULTA) ---
    if request.method == 'POST':
        form = ConsultaForm(request.POST)

        # Pega os dados que o JavaScript enviou
        data_str = request.POST.get('data_selecionada')
        hora_str = request.POST.get('hora_selecionada')

        if form.is_valid() and data_str and hora_str:
            try:
                # Combina "2025-11-07" e "09:50" em um objeto datetime
                data_horario = datetime.datetime.fromisoformat(f"{data_str}T{hora_str}")
                # Torna o datetime "aware" (consciente do fuso horário)
                data_horario_aware = timezone.make_aware(data_horario)
            except ValueError:
                messages.error(request, "Data ou hora inválida.")
                # Recarrega a página (cai no GET)
            else:
                # Cria a consulta
                consulta = form.save(commit=False)
                consulta.psicologo = psicologo
                consulta.paciente = paciente
                consulta.data_horario = data_horario_aware
                consulta.status = 'confirmado'

                try:
                    consulta.save() # Tenta salvar
                    messages.success(request, f"Consulta agendada com sucesso para {data_horario_aware.strftime('%d/%m/%Y às %H:%M')}!")
                    return redirect('root') # Mude para "minhas-consultas"
                except Exception as e:
                    # Pega o erro de unique_together
                    messages.error(request, "Este horário não está mais disponível. Por favor, tente outro.")
                    # Recarrega a página (cai no GET)
        else:
             messages.error(request, "Formulário inválido. Tente novamente.")

    # --- LÓGICA DO GET (MOSTRAR A PÁGINA) ---

    # Pega o mês e ano da URL (ou usa o atual)
    today = datetime.date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Gera o HTML do calendário
    cal = PacienteCalendar(year, month).formatmonth(withyear=True)

    # Lógica de navegação
    next_month = (datetime.date(year, month, 1) + datetime.timedelta(days=32)).replace(day=1)
    prev_month = (datetime.date(year, month, 1) - datetime.timedelta(days=1)).replace(day=1)

    context = {
        'psicologo': psicologo,
        'form': ConsultaForm(),
        'calendar': mark_safe(cal), # Passa o HTML do calendário
        'nav_next': {'year': next_month.year, 'month': next_month.month},
        'nav_prev': {'year': prev_month.year, 'month': prev_month.month},
    }
    return render(request, 'agendamento.html', context)

# API para retornar um Json com os horarios disponíveis de cada psicologo
def get_horarios_disponiveis(request, psicologo_id):
    # 1. Pegar a data da query string (ex: ?data=2025-11-07)
    data_str = request.GET.get('data')
    print(data_str)
    try:
        # Converte a string "YYYY-MM-DD" em um objeto data
        data = datetime.date.fromisoformat(data_str)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Data inválida ou não fornecida'}, status=400)

    # 2. Encontrar o dia da semana (0=Dom, 1=Seg, ... 6=Sab)
    # Usamos a lógica que você já definiu no seu modelo DIAS_CHOICES
    dia_semana_modelo = data.weekday()  # weekday() do Python: Seg=0... Dom=6
    if dia_semana_modelo == 6: # Converte Domingo (6) para 0
         dia_semana_modelo = 0
    else:
         dia_semana_modelo += 1 # Ajusta Seg-Sab para 1-6

    psicologo = get_object_or_404(Psicologo, pk=psicologo_id)

    # 3. Buscar os slots "teóricos" (a disponibilidade que o psicólogo marcou)
    # Assumindo que você usou meu modelo simplificado do grid (slot a slot)
    slots_disponiveis_obj = DisponibilidadePsicologo.objects.filter(
        psicologo=psicologo,
        dia_semana=dia_semana_modelo
    ).values_list('hora_inicio', flat=True) # Pega só os horários

    # Converte para um conjunto (Set) para facilitar a subtração
    # Ex: {datetime.time(9, 0), datetime.time(9, 50), ...}
    slots_teoricos = set(slots_disponiveis_obj)

    # 4. Buscar as consultas *já marcadas* para aquele dia
    consultas_marcadas_obj = Consulta.objects.filter(
        psicologo=psicologo,
        data_horario__date=data, # Filtra pelo dia
        status='confirmado'      # Considera apenas as confirmadas
    ).values_list('data_horario__time', flat=True) # Pega só a parte da "hora"

    consultas_marcadas = set(consultas_marcadas_obj)

    # 5. A LÓGICA: Subtrair os marcados dos teóricos
    horarios_livres = sorted(list(slots_teoricos - consultas_marcadas))

    # 6. Formatar para JSON (ex: ["09:00", "09:50", "14:00"])
    horarios_formatados = [t.strftime('%H:%M') for t in horarios_livres]

    return JsonResponse({'horarios_disponiveis': horarios_formatados})

@login_required
def agenda_paciente_view(request):
    try:
        # 1. Identificar o paciente logado
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        messages.error(request, "Perfil de paciente não encontrado.")
        return redirect('user-dashboard') # Mude para sua página inicial

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
        paciente=paciente,
        data_horario__date__range=(start_of_week, end_of_week),
        status='confirmado'
    ).select_related('psicologo', 'psicologo__usuario') # Otimiza a busca

    # 6. Processar as consultas para o template
    consultas_processadas = []
    for consulta in consultas:
        # Presume que a duração vem do perfil do psicólogo
        # ADICIONE 'duracao_minutos' AO SEU MODELO Psicologo se não existir
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
    
    return render(request, 'agenda_paciente.html', context)

@login_required
def consulta_detalhe_paciente(request, consulta_id):
    """
    Busca os detalhes de uma consulta para carregar no modal.
    Esta view retorna APENAS o HTML parcial.
    """
    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        return HttpResponse("Acesso não autorizado.", status=403)

    # Garante que a consulta existe E pertence ao paciente logado
    consulta = get_object_or_404(
        Consulta,
        pk=consulta_id,
        paciente=paciente 
    )
    
    # Renderiza o template parcial que vamos criar
    return render(request, 'partials/_modal_consulta_paciente.html', {
        'consulta': consulta
    })

@login_required
def cancelar_consulta_paciente(request, consulta_id):
    """
    Permite que o paciente cancele uma consulta.
    Redireciona de volta para a agenda do paciente.
    """
    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        messages.error(request, "Acesso não autorizado.")
        return redirect('user-dashboard')

    consulta = get_object_or_404(
        Consulta,
        pk=consulta_id,
        paciente=paciente
    )

    # Apenas permite cancelar se a consulta ainda não ocorreu
    if consulta.data_horario > timezone.now():
        if consulta.data_horario - timezone.now() < datetime.timedelta(hours=24):
            messages.error(request, "Consultas só podem ser canceladas com pelo menos 24 horas de antecedência.")
            return redirect('agenda_paciente')
        consulta.status = 'cancelado'
        consulta.save()
        messages.success(request, "Consulta cancelada com sucesso.")
    else:
        messages.error(request, "Não é possível cancelar consultas passadas.")

    return redirect('agenda_paciente')


@login_required
def perfil_paciente(request, pk):
    # Pega o paciente pelo ID ou dá erro 404
    paciente = get_object_or_404(Paciente, pk=pk)

    # CORREÇÃO 1: Trocamos 'paciente.user' por 'paciente.usuario'
    if paciente.usuario != request.user:
        messages.error(request, "Você não tem permissão para editar este perfil.")
        return redirect('user-dashboard') # Garante que volta para a dashboard correta

    # Se clicou no botão "Salvar Alterações" (POST)
    if request.method == 'POST':
        user = request.user
        
        # 1. Atualiza dados do USUÁRIO (Login, Email, Nome)
        nome_completo = request.POST.get('nome')
        email = request.POST.get('email')
        
        if nome_completo:
            nomes = nome_completo.split(' ', 1)
            user.first_name = nomes[0]
            user.last_name = nomes[1] if len(nomes) > 1 else ''
        
        if email:
            user.email = email
            
        user.save() # Salva na tabela de autenticação

        # 2. Atualiza dados do PACIENTE (Telefone, Endereço, etc)
        paciente.telefone = request.POST.get('telefone')
        paciente.cpf = request.POST.get('cpf')
        paciente.cep = request.POST.get('cep')
        paciente.endereco = request.POST.get('endereco')
        
        # Data de nascimento (evita erro se vier vazio)
        data_nascimento = request.POST.get('nascimento')
        if data_nascimento:
            paciente.data_nascimento = data_nascimento
            
        paciente.save() # Salva na tabela de paciente

        messages.success(request, "Perfil atualizado com sucesso!")
        
        # CORREÇÃO 2: Nome da URL ajustado para 'perfil-paciente' igual ao urls.py
        return redirect('perfil-paciente', pk=pk)

    # Se for apenas entrar na página (GET)
    # CORREÇÃO 3: Nome do arquivo ajustado para 'perfil_paciente.html' (com underscore)
    return render(request, 'perfil-paciente.html', {'paciente': paciente})