from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Convenio, Especialidade, Sala,
    Medico, Paciente, Disponibilidade, Consulta, RegistroProntuario
)

# Register your models here.

class PacienteInline(admin.StackedInline):
    model = Paciente
    can_delete = False
    verbose_name_plural = 'Perfil de Paciente'

class MedicoInline(admin.StackedInline):
    model = Medico
    can_delete = False
    verbose_name_plural = 'Perfil de Médico'

class CustomUserAdmin(UserAdmin):
    inlines = (PacienteInline, MedicoInline) 

    list_display = ('username', 'email', 'tipo_usuario', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tipo_usuario',)}),
    )

admin.site.register(Usuario, CustomUserAdmin)

admin.site.register(Convenio)
admin.site.register(Especialidade)
admin.site.register(Sala)
admin.site.register(Disponibilidade)
admin.site.register(Consulta)
admin.site.register(RegistroProntuario)
