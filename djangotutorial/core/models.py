from django.db import models
from django.conf import settings


class Pessoal(models.Model):
    # Vincula o perfil a um usuario do Django
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        null=True,
        blank=True,
    )

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    curso = models.CharField(max_length=200)
    periodo = models.CharField(max_length=50)
    email = models.EmailField()
    git = models.URLField(blank=True)
    linked = models.URLField(blank=True)
    imagem = models.ImageField(upload_to='perfil/')

    class Meta:
        verbose_name = 'Perfil Pessoal'
        verbose_name_plural = 'Perfis Pessoais'

    def __str__(self):
        return self.nome
