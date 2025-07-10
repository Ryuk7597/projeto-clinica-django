from django.shortcuts import render, redirect
from .forms import PacienteCreationForm 

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