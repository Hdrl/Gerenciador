from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Prefetch
from Atividades.models import  Problema, Projeto, Demanda, OrdemServico, Atividade, Equipamento, ProdutoFabricado
from Atividades.forms import ProjetoForm, DemandaForm, OrdemServicoForm, AtividadeForm
from django.http import JsonResponse
from django.contrib import messages
import json
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.views import LogoutView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from Atividades.services import processar_lista_seriais

def login_view(request):
    if request.user.is_authenticated:
        return redirect('atividades:index')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('atividades:index')
        else:
            messages.error(request, 'Usuário ou senha inválidos. Tente novamente.')
            
    form = AuthenticationForm()
    return render(request, 'Atividades/login.html', {'form': form})

class CustomLogoutView(LogoutView):
    next_page = 'atividades:login' 

@login_required
def index(request):
    prefetch_demandas_com_produtos = Prefetch(
        'demandas',
        queryset=Demanda.objects.select_related('produto').order_by('finalizado', '-id'),
        to_attr='todas_demandas'
    )

    projetos_com_demandas = Projeto.objects.all().prefetch_related(
        prefetch_demandas_com_produtos
    )
    
    context = {
        'projetos': projetos_com_demandas,
    }
    return render(request, 'Atividades/index.html', context)

@login_required
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

@login_required
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

@login_required
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
    return render(request, 'Atividades/listar_modelo.html', context)

@login_required
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

@login_required
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
    return render(request, 'Atividades/listar_modelo.html', context)

@login_required
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

@login_required
@require_POST
def editar_demanda(request, id):
    CAMPOS_PERMITIDOS = ['finalizado', 'descricao', 'prioridade']
    try:
        demanda = Demanda.objects.get(id=id)
        data = json.loads(request.body)
        campos_atualizados = []
        for campo, valor in data.items():
            if campo in CAMPOS_PERMITIDOS:
                setattr(demanda, campo, valor)
                campos_atualizados.append(campo)
            else:
                return JsonResponse({'erro': f'Campo "{campo}" não pode ser atualizado.'}, status=400)
        if campos_atualizados:
            demanda.save()
            return JsonResponse({'status': 'sucesso','mensagem': 'Demanda atualizada com sucesso.', 'campos_atualizados': campos_atualizados})
        else:
            return JsonResponse({'status':'erro', 'mensagem': 'Nenhum campo válido para atualizar.'}, status=400)
    except Demanda.DoesNotExist:
        return JsonResponse({'erro': 'Demanda não encontrada.'}, status=404)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=400)

@login_required
def listar_atividade(request):
    field_list = ['tipoAtividade', 'dataInicial', 'dataFinal', 'responsavel', 'projeto', 'situacao']

    context = {
        'querys': Atividade.objects.filter(excluido=False),
        'verbose_name': Atividade._meta.verbose_name,
        'verbose_name_plural': Atividade._meta.verbose_name_plural,
        'field_headers': [Atividade._meta.get_field(f).verbose_name for f in field_list],
        'field_names': field_list,
        'link_adcionar': 'atividades:adcionar_atividade',
    }
    return render(request, 'Atividades/atividades.html', context)

def adcionar_atividade(request):
    if request.method == 'POST':
        form = AtividadeForm(request.POST, user=request.user)
        serials_json = request.POST.get('serials_list_json')

        if form.is_valid():
            atividade = form.save(commit=False)
            atividade.responsavel = request.user
            atividade.dataInicial = form.cleaned_data['dataInicial']
            # Salva a atividade para ter um ID
            atividade.save() 
            
            if serials_json:
                try:
                    serials_list = json.loads(serials_json)
                    # --- CHAME O SERVIÇO ---
                    equipamentos = processar_lista_seriais(atividade, serials_list, form)
                    
                    if not form.errors:
                        # O serviço validou tudo, agora podemos salvar
                        atividade.equipamentos.set(equipamentos)
                        
                except Exception as e:
                    form.add_error(None, f"Erro inesperado ao processar seriais: {e}")

            if not form.errors:
                return redirect('atividades:listar_atividade')
        
        # Se o form for inválido (ou o serviço adicionar erros),
        # ele renderiza o template novamente
    else:
        form = AtividadeForm(user=request.user)

    context = {
        'form': form,
        'verbose_name': "Adicionar Atividade",
        'initial_serials_json': '[]' # Garante que a página de 'adicionar' tenha o JSON vazio
    }
    return render(request, 'Atividades/adcionar_modelo.html', context)


def editar_atividade(request, id):
    atividade = get_object_or_404(Atividade, id=id)

    if request.method == 'POST':
        form = AtividadeForm(request.POST, instance=atividade, user=request.user)
        serials_json = request.POST.get('serials_list_json')

        if form.is_valid():
            atividade = form.save() # Pode salvar direto
            
            if serials_json:
                try:
                    serials_list = json.loads(serials_json)
                    # --- CHAME O MESMO SERVIÇO ---
                    equipamentos = processar_lista_seriais(atividade, serials_list, form)

                    if not form.errors:
                        # O serviço validou tudo
                        atividade.equipamentos.set(equipamentos)

                except Exception as e:
                    form.add_error(None, f"Erro inesperado ao processar seriais: {e}")

            if not form.errors:
                return redirect('atividades:listar_atividade')

    else:
        form = AtividadeForm(instance=atividade, user=request.user)

    # Lógica do GET (serialização para o JS)
    equipamentos_atuais = atividade.equipamentos.all()
    lista_inicial_seriais = []
    for equip in equipamentos_atuais:
        lista_inicial_seriais.append({
            'produtoId': equip.produto.id,
            'produtoNome': str(equip.produto),
            'serial': equip.numero_serie
        })
    initial_serials_json = json.dumps(lista_inicial_seriais)

    context = {
        'form': form,
        'verbose_name': f"Editar Atividade: {atividade.id}",
        'initial_serials_json': initial_serials_json 
    }
    return render(request, 'Atividades/adcionar_modelo.html', context)

@login_required
def excluir_atividade(request, id):
    try:
        atividade = Atividade.objects.get(id=id)
        atividade.excluido = True
        atividade.save()
        messages.success(request, 'Atividade excluída com sucesso.')
    except Atividade.DoesNotExist:
        messages.error(request, 'Atividade não encontrada.')
    return redirect('atividades:listar_atividade')

@login_required
def verificar_equipamento_status(request):
    serial_num = request.GET.get('serial', None)
    if not serial_num:
        return JsonResponse({'status': 'erro', 'message': 'Nenhum serial fornecido.'}, status=400)

    try:
        equipamento = Equipamento.objects.get(numero_serie=serial_num)
        
        # 2. VERIFICA SE JÁ FOI MONTADO
        # (Procura por qualquer atividade 'M' ligada a este equipamento)
        foi_montado = equipamento.atividades.filter(tipoAtividade='M').exists()
        
        # 3. VERIFICA SE JÁ FOI EMBALADO
        foi_embalado = equipamento.atividades.filter(tipoAtividade='E').exists()

        if foi_embalado:
            # Já foi embalado, não pode embalar de novo
            return JsonResponse({
                'status': 'erro', 
                'message': f'Equipamento {serial_num} JÁ FOI EMBALADO.'
            }, status=400)
            
        if foi_montado:
            # OK! Foi montado e não foi embalado.
            return JsonResponse({
                'status': 'ok', 
                'message': f'Equipamento {serial_num} pronto para embalagem.',
                'equipamento_id': equipamento.id,
                'produto_nome': str(equipamento.produto) # Nome do produto
            })
        else:
            # Não foi montado
            return JsonResponse({
                'status': 'erro', 
                'message': f'Equipamento {serial_num} NÃO passou pela Montagem.'
            }, status=400)
            
    except Equipamento.DoesNotExist:
        # 4. Não encontrado
        return JsonResponse({
            'status': 'nao_encontrado', 
            'message': f'Serial {serial_num} não encontrado no sistema.'
        }, status=404)
    except Exception as e:
        return JsonResponse({'status': 'erro', 'message': str(e)}, status=500)
    

@login_required
def verificar_serial_montagem(request):
    serial_num = request.GET.get('serial', None)
    if not serial_num:
        return JsonResponse({'status': 'erro', 'message': 'Nenhum serial fornecido.'}, status=400)

    # Verifica se um equipamento com este serial JÁ EXISTE
    if Equipamento.objects.filter(numero_serie=serial_num).exists():
        # Se existe, É UM ERRO para a montagem
        return JsonResponse({
            'status': 'erro', 
            'message': f'Serial {serial_num} JÁ EXISTE no sistema e não pode ser montado novamente.'
        }, status=400) # 400 = Bad Request
    else:
        # Não existe, está livre para montagem
        return JsonResponse({
            'status': 'ok',
            'message': f'Serial {serial_num} está disponível.'
        })