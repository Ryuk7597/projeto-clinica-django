from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PacienteCreationForm
from django.contrib.auth import logout
from .models import Medico, Disponibilidade, Consulta, Paciente, Sala
from django.contrib import messages
from datetime import date, datetime, timedelta

from dependency_injector.wiring import inject, Provide
from .containers import AppContainer
from .services import NotificationService

#Injeção de Dependência
@login_required
@inject
def agendar_consulta(
    request,
    medico_id,
    horario_str,
    notification_service: NotificationService = Provide[AppContainer.notification_service],
):
    medico = get_object_or_404(Medico, pk=medico_id)
    paciente = get_object_or_404(Paciente, usuario=request.user)
    horario_consulta = datetime.strptime(horario_str, '%Y-%m-%d-%H-%M')
    sala = Sala.objects.first()

    try:
        Consulta.objects.create(...)

        mensagem = f'Sua consulta com Dr(a). {medico.nome_completo} foi agendada para {horario_consulta.strftime("%d/%m/%Y às %H:%M")}.'
        notification_service.send_notification(request.user.email, mensagem)

        messages.success(request, 'Consulta agendada com sucesso!')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro: {e}')

    return redirect('dashboard_paciente')

# Create your views here.
def home(request):
    return render(request, 'clinica/home.html')

@inject
def paciente_cadastro(
    request,
    notification_service: NotificationService = Provide[AppContainer.notification_service],
):
    if request.method == 'POST':
        form = PacienteCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save() 

            mensagem = f'Bem-vindo à nossa clínica, {usuario.username}! Sua conta foi criada com sucesso.'
            notification_service.send_notification(usuario.email, mensagem)

            messages.success(request, 'Cadastro realizado com sucesso! Por favor, faça o login.')
            return redirect('login')
    else:
        form = PacienteCreationForm()

    return render(request, 'clinica/cadastro.html', {'form': form})

@login_required
def dashboard_paciente(request):
    return render(request, 'clinica/dashboard_paciente.html')

@login_required
def listar_medicos(request):
    medicos = Medico.objects.all()
    return render(request, 'clinica/listar_medicos.html', {'medicos': medicos})

@login_required
def detalhes_medico(request, medico_id):
    medico = get_object_or_404(Medico, pk=medico_id)
    disponibilidades = Disponibilidade.objects.filter(medico=medico).order_by('dia_semana', 'hora_inicio')

    horarios_disponiveis = []
    duracao_consulta = timedelta(minutes=30)
    hoje = date.today()

    for i in range(7):
        dia_atual = hoje + timedelta(days=i)
        dia_da_semana_atual = dia_atual.isoweekday()

        consultas_no_dia = Consulta.objects.filter(
            medico=medico,
            data_hora__date=dia_atual
        ).values_list('data_hora', flat=True)

        for d in disponibilidades.filter(dia_semana=dia_da_semana_atual):
            hora_inicio = datetime.combine(dia_atual, d.hora_inicio)
            hora_fim = datetime.combine(dia_atual, d.hora_fim)

            hora_slot = hora_inicio
            while hora_slot < hora_fim:
                if hora_slot not in consultas_no_dia:
                    horarios_disponiveis.append(hora_slot)
                hora_slot += duracao_consulta

    contexto = {
        'medico': medico,
        'horarios_disponiveis': horarios_disponiveis,
    }
    return render(request, 'clinica/detalhes_medico.html', contexto)

@login_required
@inject
def agendar_consulta(
    request,
    medico_id,
    horario_str,
    notification_service: NotificationService = Provide[AppContainer.notification_service],
):
    medico = get_object_or_404(Medico, pk=medico_id)
    paciente = get_object_or_404(Paciente, usuario=request.user)
    horario_consulta = datetime.strptime(horario_str, '%Y-%m-%d-%H-%M')
    sala = Sala.objects.first()

    if not sala:
        messages.error(request, 'Erro: Nenhuma sala de atendimento foi configurada no sistema.')
        return redirect('detalhes_medico', medico_id=medico_id)

    try:
        Consulta.objects.create(
            paciente=paciente,
            medico=medico,
            sala=sala,
            data_hora=horario_consulta
        )

        mensagem = f'Sua consulta com Dr(a). {medico.nome_completo} foi agendada para {horario_consulta.strftime("%d/%m/%Y às %H:%M")}.'
        notification_service.send_notification(request.user.email, mensagem)

        messages.success(request, f'Consulta agendada com sucesso!')

    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado ao agendar a consulta: {e}')

    return redirect('dashboard_paciente')