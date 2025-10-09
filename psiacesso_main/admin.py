from django.contrib import admin
from contas.models import Paciente, Psicologo

from contas.models import Especialidade


# Crie uma classe para customizar a exibição no admin (Opcional, mas recomendado)
@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')  # Campos que aparecerão na lista
    search_fields = ('nome',)             # Adiciona uma barra de busca pelo campo 'nome'

# Registre os outros modelos (se ainda não o fez)
admin.site.register(Psicologo)
admin.site.register(Paciente)
