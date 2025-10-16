from django import forms
from Atividades.models import Projeto, Demanda

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'status', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_final': forms.DateInput(attrs={'type': 'date'}),
        }

class DemandaForm(forms.ModelForm):
    class Meta:
        model = Demanda
        fields = ['nome', 'quantidade', 'produto']