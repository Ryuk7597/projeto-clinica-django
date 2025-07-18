from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Usuario, Paciente, Medico, Especialidade, Consulta, Disponibilidade, RegistroProntuario


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


class MedicoUserCreationForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=255, required=True)
    crm = forms.CharField(max_length=20, required=True)
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidade.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo_usuario = 'medico'
        usuario.is_staff = True 
        usuario.save()

        medico = Medico.objects.create(
            usuario=usuario,
            nome_completo=self.cleaned_data.get('nome_completo'),
            crm=self.cleaned_data.get('crm'),
        )

        medico.especialidades.set(self.cleaned_data.get('especialidades'))

        return usuario

class MedicoUpdateForm(forms.ModelForm):
    especialidades = forms.ModelMultipleChoiceField(
        queryset=Especialidade.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Medico
        fields = ['nome_completo', 'crm', 'especialidades']


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'medico', 'sala', 'data_hora', 'status']
        widgets = {
            'data_hora': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }


class DisponibilidadeForm(forms.ModelForm):
    DIA_SEMANA_CHOICES = [
        (1, 'Segunda-feira'),
        (2, 'Terça-feira'),
        (3, 'Quarta-feira'),
        (4, 'Quinta-feira'),
        (5, 'Sexta-feira'),
        (6, 'Sábado'),
        (7, 'Domingo'),
    ]

    dia_semana = forms.ChoiceField(choices=DIA_SEMANA_CHOICES)

    class Meta:
        model = Disponibilidade
        fields = ['medico', 'dia_semana', 'hora_inicio', 'hora_fim']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

class ProntuarioForm(forms.ModelForm):
    class Meta:
        model = RegistroProntuario
        fields = ['descricao_atendimento', 'prescricao']
        widgets = {
            'descricao_atendimento': forms.Textarea(attrs={'rows': 5}),
            'prescricao': forms.Textarea(attrs={'rows': 3}),
        }