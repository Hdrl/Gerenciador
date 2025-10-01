from django.urls import path
from . import views

app_name = 'Atividades'

urlpatterns = [
    path('', views.index, name='index'),
]