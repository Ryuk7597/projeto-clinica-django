from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PacienteCreationForm
from django.contrib.auth import logout
from .models import Medico

# Create your views here.
def home(request):
    return render(request, 'clinica/home.html')

def paciente_cadastro(request):
    if request.method == 'POST':
        form = PacienteCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PacienteCreationForm()

    return render(request, 'clinica/cadastro.html', {'form': form})

@login_required
def dashboard_paciente(request):
    # Por enquanto, apenas renderiza o template
    return render(request, 'clinica/dashboard_paciente.html')

@login_required
def listar_medicos(request):
    # Busca todos os objetos Medico no banco de dados
    medicos = Medico.objects.all()
    # Envia a lista de medicos para o template
    return render(request, 'clinica/listar_medicos.html', {'medicos': medicos})