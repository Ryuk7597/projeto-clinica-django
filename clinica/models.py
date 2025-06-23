from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# 1. Tabela Usuario
class Usuario(AbstractUser):
    # Definição do tipo de usuário
    TIPO_USUARIO_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('recepcionista', 'Recepcionista'),
    ]
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='paciente')

# 2. Tabela Convenio
class Convenio(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

# 3. Tabela Especialidade
class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome

# 4. Tabela Sala
class Sala(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome

# 5. Tabela Medico
class Medico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    nome_completo = models.CharField(max_length=255)
    crm = models.CharField(max_length=20, unique=True)
    especialidades = models.ManyToManyField(Especialidade) # Relação N-M direta

    def __str__(self):
        return self.nome_completo

# 6. Tabela Paciente
class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    convenio = models.ForeignKey(Convenio, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nome_completo

# 7. Tabela Disponibilidade
class Disponibilidade(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    dia_semana = models.IntegerField() # Ex: 1=Segunda, 2=Terça...
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    def __str__(self):
        return f"Dr(a). {self.medico.nome_completo} - Dia: {self.dia_semana}"

# 8. Tabela Consulta
class Consulta(models.Model):
    STATUS_CHOICES = [
        ('Agendada', 'Agendada'),
        ('Realizada', 'Realizada'),
        ('Cancelada', 'Cancelada'),
    ]
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Agendada')
    data_agendamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consulta de {self.paciente.nome_completo} com Dr(a). {self.medico.nome_completo} em {self.data_hora}"

# 9. Tabela RegistroProntuario
class RegistroProntuario(models.Model):
    consulta = models.OneToOneField(Consulta, on_delete=models.CASCADE)
    descricao_atendimento = models.TextField()
    prescricao = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prontuário para a consulta {self.consulta.id}"