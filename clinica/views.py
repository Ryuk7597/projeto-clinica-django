from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PacienteCreationForm, MedicoUserCreationForm, MedicoUpdateForm 
from django.contrib.auth import logout
from .models import Medico, Disponibilidade, Consulta, Paciente, Sala
from django.contrib import messages
from datetime import date, datetime, timedelta

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView
from .models import Convenio, Especialidade, Sala, Medico



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


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    

class GerenciamentoView(AdminRequiredMixin, TemplateView):
    template_name = 'clinica/gerenciamento.html'


class ConvenioListView(AdminRequiredMixin, ListView):
    model = Convenio
    template_name = 'clinica/convenio_list.html'
    context_object_name = 'convenios'

class ConvenioCreateView(AdminRequiredMixin, CreateView):
    model = Convenio
    template_name = 'clinica/convenio_form.html'
    fields = ['nome'] 
    success_url = reverse_lazy('convenio_list') 

class ConvenioUpdateView(AdminRequiredMixin, UpdateView):
    model = Convenio
    template_name = 'clinica/convenio_form.html'
    fields = ['nome']
    success_url = reverse_lazy('convenio_list')

class ConvenioDeleteView(AdminRequiredMixin, DeleteView):
    model = Convenio
    template_name = 'clinica/convenio_confirm_delete.html'
    success_url = reverse_lazy('convenio_list')



class EspecialidadeListView(AdminRequiredMixin, ListView):
    model = Especialidade
    template_name = 'clinica/especialidade_list.html'
    context_object_name = 'especialidades'

class EspecialidadeCreateView(AdminRequiredMixin, CreateView):
    model = Especialidade
    template_name = 'clinica/especialidade_form.html'
    fields = ['nome']
    success_url = reverse_lazy('especialidade_list')

class EspecialidadeUpdateView(AdminRequiredMixin, UpdateView):
    model = Especialidade
    template_name = 'clinica/especialidade_form.html'
    fields = ['nome']
    success_url = reverse_lazy('especialidade_list')

class EspecialidadeDeleteView(AdminRequiredMixin, DeleteView):
    model = Especialidade
    template_name = 'clinica/especialidade_confirm_delete.html'
    success_url = reverse_lazy('especialidade_list')


class SalaListView(AdminRequiredMixin, ListView):
    model = Sala
    template_name = 'clinica/sala_list.html'
    context_object_name = 'salas'

class SalaCreateView(AdminRequiredMixin, CreateView):
    model = Sala
    template_name = 'clinica/sala_form.html'
    fields = ['nome', 'descricao'] 
    success_url = reverse_lazy('sala_list')

class SalaUpdateView(AdminRequiredMixin, UpdateView):
    model = Sala
    template_name = 'clinica/sala_form.html'
    fields = ['nome', 'descricao']
    success_url = reverse_lazy('sala_list')

class SalaDeleteView(AdminRequiredMixin, DeleteView):
    model = Sala
    template_name = 'clinica/sala_confirm_delete.html'
    success_url = reverse_lazy('sala_list')


class MedicoListView(AdminRequiredMixin, ListView):
    model = Medico
    template_name = 'clinica/medico_list.html'
    context_object_name = 'medicos'

class MedicoCreateView(AdminRequiredMixin, CreateView):
    form_class = MedicoUserCreationForm
    template_name = 'clinica/medico_form.html'
    success_url = reverse_lazy('medico_list')

class MedicoUpdateView(AdminRequiredMixin, UpdateView):
    model = Medico
    form_class = MedicoUpdateForm
    template_name = 'clinica/medico_form.html'
    success_url = reverse_lazy('medico_list')

class MedicoDeleteView(AdminRequiredMixin, DeleteView):
    model = Medico
    template_name = 'clinica/medico_confirm_delete.html'
    success_url = reverse_lazy('medico_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        usuario_a_deletar = self.object.usuario

        success_url = self.get_success_url()

        try:
            usuario_a_deletar.delete()
            messages.success(request, f'O médico "{self.object.nome_completo}" e sua conta de usuário foram excluídos com sucesso.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao excluir o médico: {e}')

        return HttpResponseRedirect(success_url)

