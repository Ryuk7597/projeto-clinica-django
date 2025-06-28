from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Usuario, Paciente

class PacienteCreationForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=255, help_text='Seu nome completo.')
    cpf = forms.CharField(max_length=14, help_text='Seu CPF (apenas números).')
    data_nascimento = forms.DateField(help_text='Sua data de nascimento (DD/MM/AAAA).')

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo_usuario = 'paciente'
        if commit:
            usuario.save()
            Paciente.objects.create(
                usuario=usuario,
                nome_completo=self.cleaned_data.get('nome_completo'),
                cpf=self.cleaned_data.get('cpf'),
                data_nascimento=self.cleaned_data.get('data_nascimento'),
            )
        return usuario       