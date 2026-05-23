from rest_framework import serializers
from .models import Tarefa


class TarefaSerializer(serializers.ModelSerializer):
    # Exibe o username do responsavel (somente leitura)
    responsavel = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'descricao', 'concluida', 'criado_em', 'responsavel']
        read_only_fields = ['id', 'criado_em', 'responsavel']