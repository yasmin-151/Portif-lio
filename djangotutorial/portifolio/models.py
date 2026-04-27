from django.db import models


class Certificado(models.Model):
    descricao = models.CharField(max_length=255)

    def __str__(self):
        return self.descricao

class Projeto(models.Model):
    TIPO_CHOICES = [
        ('PESSOAL', 'Pessoal'),
        ('DISCIPLINA', 'Disciplina'),
    ]

    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    link_git = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.nome} ({self.tipo})"