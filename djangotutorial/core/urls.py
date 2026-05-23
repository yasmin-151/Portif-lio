from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # API do perfil
    path('api/perfil/', views.PerfilDetail.as_view(), name='perfil-api'),
]