from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('ordemservico/', views.ordem_servico, name='lista_os'),
    path('ordemservico/novo/', views.formulario_adcionar_ordemservico, name='adcionar_ordemservico'),
    path('projeto/', views.cadastro_projeto, name='cadastro_projeto'),
    path('projeto/novo/', views.formulario_adcionar_projeto, name='adcionar_projeto'),
    path('demanda/', views.cadastro_demanda, name='cadastro_demanda'),
    path('demanda/novo/', views.formulario_adcionar_demanda, name='adcionar_demanda'),
    path('demanda/editar/<int:id>/', views.editar_demanda, name='editar_demanda'),
    path('atividade/', views.listar_atividade, name='listar_atividade'),
    path('atividade/novo/', views.adcionar_atividade, name='adcionar_atividade'),
    path('atividade/editar/<int:id>/', views.editar_atividade, name='editar_atividade'),
    path('atividade/excluir/<int:id>/', views.excluir_atividade, name='excluir_atividade'),
    path('api/verificar-equipamento/', views.verificar_equipamento_status, name='verificar_equipamento_status'),
    path('api/verificar-serial-montagem/', views.verificar_serial_montagem, name='verificar_serial_montagem'),
]