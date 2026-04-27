from django.db import models

class Pessoal(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    curso = models.CharField(max_length=100)
    periodo = models.CharField(max_length=50)
    email = models.EmailField()
    git = models.URLField(max_length=200)
    linked = models.URLField(max_length=200)
    imagem = models.ImageField(upload_to='perfil/')

    def __str__(self):
        return self.nome
