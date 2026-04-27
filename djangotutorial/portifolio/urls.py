from django.urls import path
from . import views

app_name = 'portifolio'

urlpatterns = [
    path('home/', views.home, name="home"),
    path('projetos/', views.projetos, name="projetos"),
    path('contato/',views.contato, name="contato"),
]