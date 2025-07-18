from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from datetime import date, datetime, timedelta
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_http_methods

from .models import Convenio, Especialidade, Sala, Medico, Consulta, Paciente, Disponibilidade, Disponibilidade, RegistroProntuario
from .forms import PacienteCreationForm, MedicoUserCreationForm, MedicoUpdateForm, ConsultaForm, DisponibilidadeForm, ProntuarioForm, PacienteUpdateForm

#Injeção de Dependência
from dependency_injector.wiring import inject, Provide
from .containers import AppContainer
from .services import NotificationService


def home(request):
    return render(request, 'clinica/home.html')

@login_required
def dashboard_redirect(request):
    if request.user.is_superuser:
        return redirect('gerenciamento')
    elif request.user.tipo_usuario == 'paciente':
        return redirect('dashboard_paciente')
    elif request.user.tipo_usuario == 'medico':
        return redirect('dashboard_medico')
    else:
        return redirect('home')

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
    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        paciente = None

    consultas = []
    if paciente:
        consultas = Consulta.objects.filter(paciente=paciente).order_by('data_hora')

    contexto = {'consultas': consultas}
    return render(request, 'clinica/dashboard_paciente.html', contexto)


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

    consultas_agendadas_datetime = Consulta.objects.filter(
        medico=medico,
        data_hora__gte=datetime.now()
    ).values_list('data_hora', flat=True)

    for i in range(7):
        dia_atual = hoje + timedelta(days=i)
        dia_da_semana_atual = dia_atual.isoweekday()

        for d in disponibilidades.filter(dia_semana=dia_da_semana_atual):
            hora_inicio = datetime.combine(dia_atual, d.hora_inicio)
            hora_fim = datetime.combine(dia_atual, d.hora_fim)
            hora_slot = hora_inicio
            while hora_slot < hora_fim:
                if hora_slot not in consultas_agendadas_datetime:
                    horarios_disponiveis.append(hora_slot)
                hora_slot += duracao_consulta
    
    contexto = {
        'medico': medico,
        'horarios_disponiveis': horarios_disponiveis,
    }
    return render(request, 'clinica/detalhes_medico.html', contexto)


@login_required
@require_http_methods(["POST"])
@inject
def agendar_consulta(
    request,
    medico_id,
    horario_str,
    notification_service: NotificationService = Provide[AppContainer.notification_service],
):
    if request.user.tipo_usuario != 'paciente':
        messages.error(request, 'Apenas pacientes podem agendar consultas.')
        return redirect('home')

    medico = get_object_or_404(Medico, pk=medico_id)
    paciente = get_object_or_404(Paciente, usuario=request.user)
    horario_consulta = datetime.strptime(horario_str, '%Y-%m-%d-%H-%M')

    consulta_existente_paciente = Consulta.objects.filter(
        paciente=paciente,
        data_hora=horario_consulta
    ).exists()

    if consulta_existente_paciente:
        messages.error(request, f'Você já possui uma consulta agendada para este mesmo horário ({horario_consulta.strftime("%d/%m/%Y às %H:%M")}).')
        return redirect('detalhes_medico', medico_id=medico_id)

    salas_ocupadas_ids = Consulta.objects.filter(data_hora=horario_consulta).values_list('sala__id', flat=True)
    sala_disponivel = Sala.objects.exclude(id__in=salas_ocupadas_ids).first()

    if not sala_disponivel:
        messages.error(request, f'Desculpe, não há salas disponíveis para o horário das {horario_consulta.strftime("%H:%M")}. Por favor, tente outro horário.')
        return redirect('detalhes_medico', medico_id=medico_id)

    try:
        Consulta.objects.create(
            paciente=paciente,
            medico=medico,
            sala=sala_disponivel,
            data_hora=horario_consulta
        )
        mensagem = f'Sua consulta com Dr(a). {medico.nome_completo} foi agendada para {horario_consulta.strftime("%d/%m/%Y às %H:%M")}.'
        notification_service.send_notification(request.user.email, mensagem)
        messages.success(request, 'Consulta agendada com sucesso!')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro inesperado ao agendar a consulta: {e}')

    return redirect('dashboard_redirect')


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
class MedicoRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.tipo_usuario == 'medico'

class GerenciamentoView(AdminRequiredMixin, TemplateView):
    template_name = 'clinica/gerenciamento.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_pacientes'] = Paciente.objects.count()
        context['total_medicos'] = Medico.objects.count()
        context['consultas_hoje'] = Consulta.objects.filter(data_hora__date=date.today()).count()
        return context


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


class ConsultaListView(AdminRequiredMixin, ListView):
    model = Consulta
    template_name = 'clinica/consulta_list.html'
    context_object_name = 'consultas'
    queryset = Consulta.objects.select_related('paciente', 'medico', 'sala').order_by('-data_hora')

class ConsultaCreateView(AdminRequiredMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'clinica/consulta_form.html'
    success_url = reverse_lazy('consulta_list')

class ConsultaUpdateView(AdminRequiredMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = 'clinica/consulta_form.html'
    success_url = reverse_lazy('consulta_list')

class ConsultaDeleteView(AdminRequiredMixin, DeleteView):
    model = Consulta
    template_name = 'clinica/consulta_confirm_delete.html'
    success_url = reverse_lazy('consulta_list')


class DisponibilidadeListView(AdminRequiredMixin, ListView):
    model = Disponibilidade
    template_name = 'clinica/disponibilidade_list.html'
    context_object_name = 'disponibilidades'
    queryset = Disponibilidade.objects.select_related('medico').order_by('medico', 'dia_semana')

class DisponibilidadeCreateView(AdminRequiredMixin, CreateView):
    model = Disponibilidade
    form_class = DisponibilidadeForm
    template_name = 'clinica/disponibilidade_form.html'
    success_url = reverse_lazy('disponibilidade_list')

class DisponibilidadeUpdateView(AdminRequiredMixin, UpdateView):
    model = Disponibilidade
    form_class = DisponibilidadeForm
    template_name = 'clinica/disponibilidade_form.html'
    success_url = reverse_lazy('disponibilidade_list')

class DisponibilidadeDeleteView(AdminRequiredMixin, DeleteView):
    model = Disponibilidade
    template_name = 'clinica/disponibilidade_confirm_delete.html'
    success_url = reverse_lazy('disponibilidade_list')


class ProntuarioCreateView(MedicoRequiredMixin, CreateView):
    model = RegistroProntuario
    form_class = ProntuarioForm
    template_name = 'clinica/prontuario_form.html'
    success_url = reverse_lazy('dashboard_medico') 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        consulta = get_object_or_404(Consulta, pk=self.kwargs['consulta_id'])
        context['consulta'] = consulta
        return context

    def form_valid(self, form):
        consulta = get_object_or_404(Consulta, pk=self.kwargs['consulta_id'])
        if hasattr(consulta, 'registroprontuario'):
            messages.error(self.request, 'Esta consulta já possui um registro de prontuário.')
            return redirect('dashboard_medico') 

        form.instance.consulta = consulta
        messages.success(self.request, 'Prontuário adicionado com sucesso!')
        return super().form_valid(form)

class ProntuarioUpdateView(MedicoRequiredMixin, UpdateView):
    model = RegistroProntuario
    form_class = ProntuarioForm
    template_name = 'clinica/prontuario_form.html'
    success_url = reverse_lazy('dashboard_medico')


class DashboardMedicoView(MedicoRequiredMixin, TemplateView):
    template_name = 'clinica/medico/dashboard_medico.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            medico = self.request.user.medico
            hoje = date.today()

            consultas_de_hoje = Consulta.objects.filter(
                medico=medico,
                data_hora__date=hoje
            ).order_by('data_hora')

            context['consultas_de_hoje'] = consultas_de_hoje
            context['medico'] = medico
        except Medico.DoesNotExist:
            context['consultas_de_hoje'] = []
            context['medico'] = None

        return context

class DashboardPacienteView(LoginRequiredMixin, TemplateView):
    template_name = 'clinica/paciente/dashboard_paciente.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            paciente = self.request.user.paciente
            consultas = Consulta.objects.filter(paciente=paciente).order_by('data_hora')
            context['consultas'] = consultas
        except Paciente.DoesNotExist:
            context['consultas'] = []
        return context


class PacienteListView(AdminRequiredMixin, ListView):
    model = Paciente
    template_name = 'clinica/paciente_list.html'
    context_object_name = 'pacientes'
    queryset = Paciente.objects.select_related('usuario', 'convenio').order_by('nome_completo')

class PacienteCreateAdminView(AdminRequiredMixin, CreateView):
    form_class = PacienteCreationForm
    template_name = 'clinica/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class PacienteUpdateView(AdminRequiredMixin, UpdateView):
    model = Paciente
    form_class = PacienteUpdateForm
    template_name = 'clinica/paciente_form.html'
    success_url = reverse_lazy('paciente_list')

class PacienteDeleteView(AdminRequiredMixin, DeleteView):
    model = Paciente
    template_name = 'clinica/paciente_confirm_delete.html'
    success_url = reverse_lazy('paciente_list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        usuario_a_deletar = self.object.usuario
        success_url = self.get_success_url()
        try:
            usuario_a_deletar.delete()
            messages.success(request, f'O paciente "{self.object.nome_completo}" e sua conta de usuário foram excluídos com sucesso.')
        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao excluir o paciente: {e}')
        return HttpResponseRedirect(success_url)