from django.shortcuts import render
from Atividades.models import  Problema

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
    return render(request, 'Atividades/cadastro/equipamento.html', context)  

def cadastro_problema(request):
    context = {'problemas': Problema.objects.all()}
    return render(request, 'Atividades/cadastro/problema.html', context)