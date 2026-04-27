from django.shortcuts import render
from core.models import Pessoal
from .models import Certificado, Projeto

def home(request):
    perfil = Pessoal.objects.first()
    certificados = Certificado.objects.all()
    projetos_lista = Projeto.objects.all()
    context = {
        'perfil': perfil,
        'certificados': certificados,
        'projetos': projetos_lista,
    }
    return render(request, 'portifolio/home.html', context)

def projetos(request):
    projetos_do_banco = Projeto.objects.all()
    return render(request, 'portifolio/projetos.html', {'projetos': projetos_do_banco})
def contato(request):
    return render(request, 'portifolio/contato.html')