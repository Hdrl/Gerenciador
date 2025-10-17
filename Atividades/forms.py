from django import forms
from Atividades.models import Projeto, Demanda, OrdemServico

class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'status', 'data_inicio', 'data_fim']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'type': 'date'}),
        }

class DemandaForm(forms.ModelForm):
    class Meta:
        model = Demanda
        fields = ['nome', 'quantidade', 'produto', 'projeto']

class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ['projeto', 'NFEntrada', 'defeitoInformado', 'localExecucao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }