from django.shortcuts import render
from django.utils.safestring import mark_safe
import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from contas.models import Especialidade, Psicologo
from psiacesso_main.models import Formacao, Paciente, Consulta, DisponibilidadePsicologo
from django.http import JsonResponse
from .utils import PacienteCalendar # Importe o calendário
from .forms import ConsultaForm
from django.shortcuts import get_object_or_404, render, redirect

@login_required
def dashboard(request):
    #Logica para carregar 4 psicologos mais novos
    recentes = Psicologo.objects.order_by('-id')[:4]
    
    #Pegar as consultas mais recentes    
    consultas = Consulta.objects.filter(paciente=request.user.paciente).order_by('-data_horario')[:5]
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



