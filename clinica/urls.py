# clinica/urls.py (VERSÃO FINAL E CORRIGIDA)

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='clinica/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('cadastro/', views.paciente_cadastro, name='paciente_cadastro'),

    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('paciente/dashboard/', views.DashboardPacienteView.as_view(), name='dashboard_paciente'),
    path('medico/dashboard/', views.DashboardMedicoView.as_view(), name='dashboard_medico'),

    path('agendamento/', views.listar_medicos, name='listar_medicos'),
    path('medico/<int:medico_id>/', views.detalhes_medico, name='detalhes_medico'),
    path('agendar/<int:medico_id>/<str:horario_str>/', views.agendar_consulta, name='agendar_consulta'),

    path('consulta/<int:consulta_id>/prontuario/novo/', views.ProntuarioCreateView.as_view(), name='prontuario_create'),
    path('prontuario/<int:pk>/editar/', views.ProntuarioUpdateView.as_view(), name='prontuario_update'),

    path('gerenciar/', views.GerenciamentoView.as_view(), name='gerenciamento'),


    path('gerenciar/convenios/', views.ConvenioListView.as_view(), name='convenio_list'),
    path('gerenciar/convenios/novo/', views.ConvenioCreateView.as_view(), name='convenio_create'),
    path('gerenciar/convenios/<int:pk>/editar/', views.ConvenioUpdateView.as_view(), name='convenio_update'),
    path('gerenciar/convenios/<int:pk>/excluir/', views.ConvenioDeleteView.as_view(), name='convenio_delete'),

    path('gerenciar/especialidades/', views.EspecialidadeListView.as_view(), name='especialidade_list'),
    path('gerenciar/especialidades/nova/', views.EspecialidadeCreateView.as_view(), name='especialidade_create'),
    path('gerenciar/especialidades/<int:pk>/editar/', views.EspecialidadeUpdateView.as_view(), name='especialidade_update'),
    path('gerenciar/especialidades/<int:pk>/excluir/', views.EspecialidadeDeleteView.as_view(), name='especialidade_delete'),

    path('gerenciar/salas/', views.SalaListView.as_view(), name='sala_list'),
    path('gerenciar/salas/nova/', views.SalaCreateView.as_view(), name='sala_create'),
    path('gerenciar/salas/<int:pk>/editar/', views.SalaUpdateView.as_view(), name='sala_update'),
    path('gerenciar/salas/<int:pk>/excluir/', views.SalaDeleteView.as_view(), name='sala_delete'),

    path('gerenciar/medicos/', views.MedicoListView.as_view(), name='medico_list'),
    path('gerenciar/medicos/novo/', views.MedicoCreateView.as_view(), name='medico_create'),
    path('gerenciar/medicos/<int:pk>/editar/', views.MedicoUpdateView.as_view(), name='medico_update'),
    path('gerenciar/medicos/<int:pk>/excluir/', views.MedicoDeleteView.as_view(), name='medico_delete'),

    path('gerenciar/consultas/', views.ConsultaListView.as_view(), name='consulta_list'),
    path('gerenciar/consultas/nova/', views.ConsultaCreateView.as_view(), name='consulta_create'),
    path('gerenciar/consultas/<int:pk>/editar/', views.ConsultaUpdateView.as_view(), name='consulta_update'),
    path('gerenciar/consultas/<int:pk>/cancelar/', views.ConsultaDeleteView.as_view(), name='consulta_delete'),

    path('gerenciar/disponibilidades/', views.DisponibilidadeListView.as_view(), name='disponibilidade_list'),
    path('gerenciar/disponibilidades/nova/', views.DisponibilidadeCreateView.as_view(), name='disponibilidade_create'),
    path('gerenciar/disponibilidades/<int:pk>/editar/', views.DisponibilidadeUpdateView.as_view(), name='disponibilidade_update'),
    path('gerenciar/disponibilidades/<int:pk>/excluir/', views.DisponibilidadeDeleteView.as_view(), name='disponibilidade_delete'),
    path('gerenciar/pacientes/', views.PacienteListView.as_view(), name='paciente_list'),
    path('gerenciar/pacientes/novo/', views.PacienteCreateAdminView.as_view(), name='paciente_create_admin'),
    path('gerenciar/pacientes/<int:pk>/editar/', views.PacienteUpdateView.as_view(), name='paciente_update'),
    path('gerenciar/pacientes/<int:pk>/excluir/', views.PacienteDeleteView.as_view(), name='paciente_delete'),
    
]
