from django.shortcuts import render
from django.db.models import Prefetch
from Atividades.models import  Problema, Projeto, Demanda
from Atividades.forms import ProjetoForm
from django.shortcuts import redirect

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

#post {"data1":"2025-09-30 00:00:01","data2":"2025-10-01 00:00:01"}

def cadastro_equipamento(request):
    context = {}
    return render(request, 'Atividades/cadastro/equipamento.html', context)  

def cadastro_problema(request):
    context = {'problemas': Problema.objects.all()}
    return render(request, 'Atividades/cadastro/problema.html', context)

def cadastro_projeto(request):
    context = {'projetos': Projeto.objects.all()}
    return render(request, 'Atividades/cadastro/projeto.html', context)

def formulario_adcionar_projeto(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar para a página de listagem de projetos após salvar
            return redirect('atividades:cadastro_projeto')
    context = {
        'form': ProjetoForm()
    }
    return render(request, 'Atividades/cadastro/formulario_adcionar/projeto.html', context) 

def cadastro_demanda(request):
    context = {'demandas': Demanda.objects.all()}
    return render(request, 'Atividades/cadastro/demanda.html', context)

def formulario_adcionar_demanda(request):
    if request.method == 'POST':
        form = ProjetoForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirecionar para a página de listagem de projetos após salvar
            return redirect('atividades:cadastro_demanda')
    context = {
        'form': ProjetoForm()
    }
    return render(request, 'Atividades/cadastro/formulario_adcionar/demanda.html', context)