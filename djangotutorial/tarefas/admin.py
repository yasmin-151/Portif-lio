from django.contrib import admin
from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    # Colunas exibidas na listagem
    list_display = ['titulo', 'concluida', 'criado_em']

    # Filtro lateral por status
    list_filter = ['concluida']

    # Campo de busca
    search_fields = ['titulo', 'descricao']