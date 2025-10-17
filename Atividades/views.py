from django.shortcuts import render, redirect
from django.db.models import Prefetch
from Atividades.models import  Problema, Projeto, Demanda, OrdemServico
from Atividades.forms import ProjetoForm, DemandaForm, OrdemServicoForm

def index(request):
    prefetch_demandas_com_produtos = Prefetch(
        'demandas',
        queryset=Demanda.objects.select_related('produto')
    )

    # Agora, ao buscar os projetos, aplicamos este prefetch otimizado.
    projetos_com_demandas = Projeto.objects.all().prefetch_related(
        prefetch_demandas_com_produtos
    )
    
    context = {
        'projetos': projetos_com_demandas,
    }
    return render(request, 'Atividades/index.html', context)

# Create your views here.
def ordem_servico(request):
    ordens_de_servico = [
        {'id': 1024, 'cliente': 'João da Silva', 'equipamento': 'Notebook Dell Vostro', 'data': '2025-09-28', 'status': 'Concluído'},
        {'id': 1025, 'cliente': 'Maria Oliveira', 'equipamento': 'Celular Samsung S23', 'data': '2025-09-29', 'status': 'Em Andamento'},
        {'id': 1026, 'cliente': 'Pedro Martins', 'equipamento': 'Impressora HP', 'data': '2025-09-30', 'status': 'Aguardando Peças'},
        {'id': 1027, 'cliente': 'Ana Costa', 'equipamento': 'Tablet iPad Air', 'data': '2025-10-01', 'status': 'Orçamento Aprovado'},
    ]

    context = {
        'ordens_de_servico': ordens_de_servico,
    }
    return render(request, 'Atividades/ordem_servico.html', context)

def formulario_adcionar_ordemservico(request):
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar para a página de listagem de projetos após salvar
            return redirect('atividades:cadastro_projeto')
    context = {
        'form': OrdemServicoForm(),
        'verbose_name': OrdemServico._meta.verbose_name,
    }
    return render(request, 'Atividades/adcionar_modelo.html', context) 
#post {"data1":"2025-09-30 00:00:01","data2":"2025-10-01 00:00:01"}

def cadastro_projeto(request):
    field_list = ['nome', 'descricao', 'status', 'data_inicio', 'data_fim']

    context = {
        'querys': Projeto.objects.all(),
        'verbose_name': Projeto._meta.verbose_name,
        'verbose_name_plural': Projeto._meta.verbose_name_plural,
        'field_headers': [Projeto._meta.get_field(f).verbose_name for f in field_list],
        'field_names': field_list,
        'link_adcionar': 'atividades:formulario_adcionar_projeto',
    }
    return render(request, 'Atividades/cadastro.html', context)

def formulario_adcionar_projeto(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar para a página de listagem de projetos após salvar
            return redirect('atividades:cadastro_projeto')
    context = {
        'form': ProjetoForm(),
        'verbose_name': Projeto._meta.verbose_name,
    }
    return render(request, 'Atividades/adcionar_modelo.html', context) 

def cadastro_demanda(request):
    field_list = ['produto', 'quantidade', 'projeto', 'finalizado']

    context = {
        'querys': Demanda.objects.all(),
        'verbose_name': Demanda._meta.verbose_name,
        'verbose_name_plural': Demanda._meta.verbose_name_plural,
        'field_headers': [Demanda._meta.get_field(f).verbose_name for f in field_list],
        'field_names': field_list,
        'link_adcionar': 'atividades:formulario_adcionar_demanda',
    }
    return render(request, 'Atividades/cadastro.html', context)

def formulario_adcionar_demanda(request):
    if request.method == 'POST':
        form = DemandaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('atividades:cadastro_demanda')
    context = {
        'form': DemandaForm(),
        'verbose_name': Demanda._meta.verbose_name,
    }
    return render(request, 'Atividades/adcionar_modelo.html', context)