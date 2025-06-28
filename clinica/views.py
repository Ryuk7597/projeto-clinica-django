from django.shortcuts import render, redirect
from .forms import PacienteCreationForm 

# Create your views here.
def home(request):
    return render(request, 'clinica/home.html')

def paciente_cadastro(request):
    if request.method == 'POST':
        form = PacienteCreationForm(request.POST)
        if form.is_valid():
            # A mágica acontece aqui.
            # Agora chamamos o método .save() do nosso formulário customizado,
            # que já sabe como criar o Usuário E o Paciente.
            form.save()
            return redirect('home')
    else:
        form = PacienteCreationForm()

    return render(request, 'clinica/cadastro.html', {'form': form})