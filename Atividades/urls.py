from django.urls import path
from . import views

app_name = 'Atividades'

urlpatterns = [
    path('', views.ordem_servico, name='lista_os'),
]