from django.db import models
from django.conf import settings  # Para referenciar o modelo de usuario


class Tarefa(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    concluida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    # Novo campo: quem criou a tarefa
    # null=True e blank=True para nao quebrar tarefas ja existentes
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,       # Referencia o modelo User do Django
        on_delete=models.CASCADE,       # Se o usuario for excluido, exclui as tarefas dele
        related_name='tarefas',         # Permite acessar: user.tarefas.all()
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo