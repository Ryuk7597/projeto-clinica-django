from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Convenio, Especialidade, Sala,
    Medico, Paciente, Disponibilidade, Consulta, RegistroProntuario
)

# Register your models here.

class CustomUserAdmin(UserAdmin):
    # Campos a serem exibidos na lista de usuários
    list_display = ('username', 'email', 'tipo_usuario', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo_usuario',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('tipo_usuario',)}),
    )

# Registrando os modelos
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Convenio)
admin.site.register(Especialidade)
admin.site.register(Sala)
admin.site.register(Medico)
admin.site.register(Paciente)
admin.site.register(Disponibilidade)
admin.site.register(Consulta)
admin.site.register(RegistroProntuario)