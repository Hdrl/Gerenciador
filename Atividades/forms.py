from django import forms
from Atividades.models import Projeto, Demanda, Atividade, ProdutoFabricado
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

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

class AtividadeForm(forms.ModelForm):
    produto = forms.ModelChoiceField(
        queryset=ProdutoFabricado.objects.all(), 
        empty_label="---------", 
        required=False,
        label='Produto',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    serial = forms.CharField(required=False, label='Serial', help_text='Digite o serial e pressione Enter para adicionar à lista.')
    serials_list = forms.CharField(
        required=False, 
        widget=forms.HiddenInput()
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False 
        
        self.helper.layout = Layout(
            # Linha 1 (Como antes)
            Row(
                Column('data_inicial', css_class='col-md-4'),
                Column('tipo_atividade', css_class='col-md-4'),
                Column('projeto', css_class='col-md-4'),
                css_class='mb-3'
            ),
            # Linha 2 (Como antes)
            Row(
                Column('responsavel', css_class='col-md-4'),
                Column('produto', css_class='col-md-4'),
                Column('serial', css_class='col-md-4'),
                css_class='mb-3'
            ),
        )

        # Lógica de 'disabled' (Como antes)
        if not self.instance.pk:
            if user:
                self.fields['responsavel'].initial = user
                self.fields['data_inicial'].initial = timezone.now()
            
            self.fields['responsavel'].disabled = True
            self.fields['data_inicial'].disabled = True
        else:
            self.fields['responsavel'].disabled = True
            self.fields['data_inicial'].disabled = True

        self.produto = ProdutoFabricado.objects.values_list('id', 'descricao')

    class Meta:
        model = Atividade
        
        # 1. ADICIONE 'equipamentos' À LISTA DE CAMPOS
        fields = [
          'responsavel', 'projeto', 
            'tipo_atividade'
        ]
        
        widgets = {
            # Widgets de data (Como antes)
            'dataInicial': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),
            'dataFinal': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),

        }