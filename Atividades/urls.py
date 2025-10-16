from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('', views.index, name='index'),
    path('ordemservico', views.ordem_servico, name='lista_os'),
    path('cadastro/projeto/', views.cadastro_projeto, name='cadastro_projeto'),
    path('cadastro/projeto/novo/', views.formulario_adcionar_projeto, name='formulario_adcionar_projeto'),
    path('cadastro/demanda/', views.cadastro_demanda, name='cadastro_demanda'),
    path('cadastro/demanda/novo/', views.formulario_adcionar_demanda, name='formulario_adcionar_demanda'),
]