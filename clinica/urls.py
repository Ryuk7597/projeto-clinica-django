from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.paciente_cadastro, name='paciente_cadastro'),
    path('login/', auth_views.LoginView.as_view(template_name='clinica/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_paciente, name='dashboard_paciente'),
    path('agendamento/', views.listar_medicos, name='listar_medicos'),
    
]

