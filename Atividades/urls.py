from django.urls import path
from . import views

app_name = 'atividades'

urlpatterns = [
    path('', views.ordem_servico, name='lista_os'),
    path('cadastro/equipamento/', views.cadastro_equipamento, name='cadastro_equipamento'),
    path('cadastro/problema/', views.cadastro_problema, name='cadastro_problema'),]