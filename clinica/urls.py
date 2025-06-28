from django.urls import path
from . import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.paciente_cadastro, name='paciente_cadastro'),
]

