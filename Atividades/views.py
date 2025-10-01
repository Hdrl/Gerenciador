from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'total_atividades': 15,
        'atividades_concluidas': 8,
    }
    return render(request, 'Atividades/index.html', context)