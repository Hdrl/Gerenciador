from django.contrib import admin
from .models import  AgrupamentoVolume, ItemInstalacao, OrdemProducao, Transporte ,Fornecedor, Item, MateriaPrima, ProdutoFabricado, EstruturaProduto, Projeto, Demanda, Atividade, OrdemServico, Equipamento, Endereco, Empresa, Transportadora, DefeitoComponente
from django.contrib import admin, messages
from django.utils import timezone
from .models import OrdemProducao
from decimal import Decimal
from django.contrib import admin, messages
from django.http import HttpResponse
from django.template import Context, Template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm 

class ItemInstalacaoInline(admin.TabularInline):
    model = ItemInstalacao
    fk_name = 'produto_pai'
    fields = ('item_acessorio', 'quantidade')
    raw_id_fields = ('item_acessorio',) 
    extra = 1
    verbose_name_plural = "Componentes para Instalação"

class EstruturaProdutoInline(admin.TabularInline):
    """
    Permite editar os componentes (BOM) diretamente na página do Produto Fabricado.
    'TabularInline' é mais compacto e ideal para listas de componentes.
    """
    model = EstruturaProduto
    fk_name = 'produto_pai'
    fields = ('componente_filho', 'quantidade')
    raw_id_fields = ('componente_filho',)
    extra = 1
    verbose_name = "Componente da Estrutura"
    verbose_name_plural = "Componentes para Produção"

class DemandaInline(admin.TabularInline):
    model = Demanda
    fk_name = 'projeto'
    fields = ('produto', 'quantidade_total', 'quantidade_reserva')
    extra = 1
    verbose_name = "Demanda do Projeto"
    verbose_name_plural = "Demandas do Projeto"
    raw_id_fields = ('produto',)

class AgrupamentoVolumeInline(admin.TabularInline):
    """
    Permite adicionar/ver os LOTES de volumes.
    """
    model = AgrupamentoVolume
    fk_name = 'projeto'
    # Campos que o usuário vai preencher
    fields = (
        'produto', 
        'quantidade_por_volume', 
        'numero_de_volumes', 
        'codigo_lote', 
        'data_embalado'
    )
    readonly_fields = ('codigo_lote', 'data_embalado')
    extra = 1
    verbose_name_plural = "Lotes de Volumes Embalados"
    raw_id_fields = ('produto',)

@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    """
    Configuração personalizada do Admin para Ordens de Produção.
    (VERSÃO CORRIGIDA)
    """
    #
    # SUAS ACTIONS (estão corretas e não mudam)
    #
    @admin.action(description='1. Liberar OPs selecionadas para produção')
    def marcar_como_liberada(self, request, queryset):
        # ... (seu código da action) ...
        # (Atualiza para o status correto do modelo)
        count = 0
        total = queryset.count()
        ops_para_liberar = queryset.filter(status=OrdemProducao.StatusOP.PLANEJADA)
        for op in ops_para_liberar:
            op.liberar_producao() 
            count += 1
        # ... (o resto da sua action) ...
        if count > 0:
            self.message_user(request, f"{count} de {total} OPs foram liberadas.", messages.SUCCESS)
        if count < total:
            self.message_user(request, f"{total - count} OPs já estavam em outro status e não foram liberadas.", messages.WARNING)


    @admin.action(description='2. Marcar OPs selecionadas como "Em Produção"')
    def marcar_como_iniciada(self, request, queryset):
        # (Atualiza para o status correto do modelo)
        updated_count = queryset.filter(status=OrdemProducao.StatusOP.LIBERADA).update(
            status=OrdemProducao.StatusOP.EM_PRODUCAO,
            data_inicio_real=timezone.now()
        )
        self.message_user(request, f"{updated_count} OPs foram marcadas como 'Em Produção'.", messages.SUCCESS)

    @admin.action(description='3. Concluir OPs selecionadas (Qtd. Produzida = Qtd. Planejada)')
    def marcar_como_concluida(self, request, queryset):
        # ... (seu código da action, atualizado para os status corretos) ...
        updated_count = 0
        valid_statuses = [
            OrdemProducao.StatusOP.EM_PRODUCAO, 
            OrdemProducao.StatusOP.CONTROLE_QUALIDADE
        ]
        ops_para_concluir = queryset.filter(status__in=valid_statuses)

        for op in ops_para_concluir:
            # Chama o método que criamos, em vez de lógica manual
            op.concluir_producao(quantidade_boa=op.quantidade_planejada) 
            updated_count += 1
            
        self.message_user(request, f"{updated_count} OPs foram concluídas com sucesso.", messages.SUCCESS)

    #
    # --- CORREÇÕES ABAIXO ---
    #
    
    list_display = (
        'codigo_op', # Adicionado para ficar mais fácil de ver
        'status',
        'produto',
        'quantidade_planejada',
        'data_prevista_conclusao',  # CORRETO: 'tempo_execucao_preivista' -> 'data_prevista_conclusao'
        'data_emissao',             # CORRETO: 'data_criacao' -> 'data_emissao'
    )
    
    list_filter = (
        'status',
        'data_prevista_conclusao',  # CORRETO: 'tempo_execucao_preivista' -> 'data_prevista_conclusao'
        'data_emissao',             # CORRETO: 'data_criacao' -> 'data_emissao'
        'produto',
        'projeto',
    )
    
    search_fields = (
        'codigo_op', # Adicionado
        'produto__codigo_item',
        'produto__descricao', 
        'projeto__nome', 
    )
    
    readonly_fields = (
        'codigo_op',             # Adicionado (é auto-gerado)
        'data_emissao',          # CORRETO: 'data_criacao' -> 'data_emissao'
        'data_conclusao_real',   # CORRETO: 'data_real_termino' -> 'data_conclusao_real'
        'quantidade_produzida',
        'custo_estimado',        # Adicionado (é auto-calculado)
        'custo_real',
    )

    # --- Organização do Formulário de Edição ---
    # (Este já estava correto no seu arquivo original)
    fieldsets = (
        ('Informações Principais', {
            'fields': (
                'codigo_op',
                'status',
                'produto',
                'quantidade_planejada',
            )
        }),
        ('Custos (Calculados)', {
            'fields': (
                'custo_estimado',
                'custo_real',
            )
        }),
        ('Datas', {
            'fields': (
                'data_emissao',
                'data_prevista_conclusao',
                'data_inicio_real',
                'data_conclusao_real',
            )
        }),
        ('Contexto e Responsáveis', {
            'fields': (
                'solicitante',
                'projeto',
                'demanda_origem', # Adicionado
            )
        }),
        ('Resultados e Observações', {
            'fields': (
                'quantidade_produzida',
                'observacoes',
            )
        }),
    )

    @admin.action(description='📋 Gerar Lista de Separação (BOM) para OPs selecionadas')
    def gerar_lista_separacao_producao(self, request, queryset):
        
        # 1. VALIDAÇÃO: Garante que só OPs 'Liberadas' ou 'Planejadas' entrem
        ops_validas = queryset.filter(
            status__in=[
                OrdemProducao.StatusOP.PLANEJADA, 
                OrdemProducao.StatusOP.LIBERADA
            ]
        )
        
        if not ops_validas.exists():
            self.message_user(request, 
                              "Nenhuma OP selecionada é válida (devem ser 'Planejada' ou 'Liberada').", 
                              messages.ERROR)
            return

        # 2. LÓGICA DE AGREGAÇÃO (A "EXPLOSÃO" DO BOM)
        
        # Otimiza a consulta ao banco de dados
        ops_para_processar = ops_validas.prefetch_related(
            'produto__componentes__componente_filho' # Otimização crucial
        )

        lista_materiais_agregada = {} # Dicionário para consolidar os totais
        op_codes = [] # Lista de OPs incluídas

        for op in ops_para_processar:
            op_codes.append(op.codigo_op)
            # Converte a quantidade da OP para Decimal
            qtd_a_produzir = Decimal(op.quantidade_planejada)
            
            # Pega o BOM (EstruturaProduto) do produto da OP
            # Graças ao prefetch_related, isto não gera nova consulta
            bom_do_produto = op.produto.componentes.all() 
            
            for componente in bom_do_produto:
                nome_item = componente.componente_filho.descricao
                # Pega o 'codigo_item' para referência
                cod_item = componente.componente_filho.codigo_item
                # Pega a unidade de medida
                unidade = componente.componente_filho.get_unidade_medida_display()
                
                # Calcula a quantidade necessária deste componente
                # (Qtd da OP * Qtd do BOM)
                qtd_total_componente = componente.quantidade * qtd_a_produzir
                
                # Cria uma chave única (código + nome) para o dicionário
                chave_item = f"({cod_item}) {nome_item}"
                
                # Pega o valor atual (ou 0) e soma o novo valor
                valor_anterior = lista_materiais_agregada.get(chave_item, (Decimal(0), unidade))[0]
                
                # Armazena (Quantidade Total, Unidade)
                lista_materiais_agregada[chave_item] = (valor_anterior + qtd_total_componente, unidade)

        if not lista_materiais_agregada:
            self.message_user(request, "As OPs selecionadas não possuem uma Lista de Materiais (BOM) definida.", messages.WARNING)
            return

        # 3. GERAR O PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="lista_separacao_producao.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(2*cm, height - 2*cm, "Lista de Separação para Produção")

        p.setFont("Helvetica", 9)
        p.drawString(2*cm, height - 2.7*cm, f"OPs consolidadas: {', '.join(op_codes)}")
        
        y = height - 4*cm # Posição inicial Y
        
        # Cabeçalho da tabela
        p.setFont("Helvetica-Bold", 11)
        p.drawString(2*cm, y, "Quantidade")
        p.drawString(5*cm, y, "Unidade")
        p.drawString(8*cm, y, "Item (Código e Descrição)")
        p.line(2*cm, y - 0.2*cm, width - 2*cm, y - 0.2*cm)
        y -= 0.7*cm
        
        p.setFont("Helvetica", 10)
        # Ordena a lista pelo nome do item
        itens_ordenados = sorted(lista_materiais_agregada.items())

        for item_nome, (quantidade, unidade) in itens_ordenados:
            if y < 3*cm: # Se chegar no fim da página
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 2*cm # Reseta o Y

            # Escreve a linha
            p.drawString(2*cm, y, str(quantidade))
            p.drawString(5*cm, y, str(unidade))
            p.drawString(8*cm, y, item_nome)
            y -= 0.7*cm # Próxima linha

        p.showPage()
        p.save()

        return response
    
    # --- C. Registre TODAS as suas actions ---
    actions = [
        'marcar_como_liberada',
        'marcar_como_iniciada',
        'marcar_como_concluida',
        'gerar_lista_separacao_producao', # Adicione a nova
    ]

@admin.register(Transportadora)
class TransportadoraoAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'nome_contato', 'telefone', 'observacoes')
    list_per_page = 20

@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    list_per_page = 20

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('solicitante', 'local_execucao', 'nota_entrada', 'nota_saida', 'projeto' , 'transporte')
    list_per_page = 20

@admin.register(DefeitoComponente)
class DefeitoComponenteAdmin(admin.ModelAdmin):
    list_display = ('componente', 'defeito', 'efeito', 'causa')
    list_per_page = 20
    ordering = ('componente',)

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('id_empresa', 'apelido_endereco', 'cidade', 'uf')
    list_per_page = 20
    ordering = ('-uf',)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'cnpj', 'data_cadastro']
    list_per_page = 20
    ordering = ('-data_cadastro',)

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('tipo_atividade', 'data_inicial', 'data_final', 'responsavel', 'projeto', 'status')
    search_fields = ('responsavel__username', 'projeto__nome')
    list_filter = ('tipo_atividade', 'status', 'data_inicial', 'data_final')
    list_per_page = 20

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'numero_serie', 'projeto_alocado')
    search_fields = ('produto__codigo_item', 'numero_serie', 'projeto_alocado__nome')
    list_filter = ('projeto_alocado',)
    list_per_page = 20  

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    """
    Admin para o cadastro de Fornecedores.
    """
    list_display = ('razao_social', 'cnpj')
    search_fields = ('razao_social', 'cnpj')
    list_per_page = 20

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Admin para a visualização de TODOS os itens.
    Esta visão é configurada como "somente leitura" para evitar a criação
    de itens genéricos que não sejam Matéria-Prima ou Produto Fabricado.
    """
    list_display = ('codigo_item', 'descricao', 'unidade_medida', 'tipo_especifico')
    list_display_links = ('codigo_item', 'descricao')
    list_filter = ('unidade_medida',)
    search_fields = ('codigo_item', 'descricao')
    list_per_page = 25
    
    # Ordena por código do item por padrão
    ordering = ('codigo_item',)
    
    def has_add_permission(self, request):
        # Impede que usuários criem um 'Item' genérico através desta interface.
        # A criação deve ser feita através de Matéria-Prima ou Produto Fabricado.
        return False
        
    def has_change_permission(self, request, obj=None):
        # Opcional: Impede a edição por aqui também, forçando o uso da admin correta.
        return False

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    """
    Admin para o cadastro e gerenciamento de Matérias-Primas.
    """
    list_display = ('codigo_item', 'descricao', 'preco_custo_compra', 'fornecedor_padrao')
    search_fields = ('codigo_item', 'descricao', 'fornecedor_padrao__razao_social')
    list_filter = ('fornecedor_padrao',)
    list_per_page = 25
    ordering = ('codigo_item',)
    
    readonly_fields = ('codigo_item',)
    
    # 'fieldsets' organiza o formulário de edição em seções lógicas.
    fieldsets = (
        ('Dados Gerais (Herdado de Item)', {
            'fields': ('codigo_item', 'descricao', 'unidade_medida')
        }),
        ('Dados de Compra', {
            'fields': ('preco_custo_compra', 'fornecedor_padrao')
        }),
    )

@admin.register(ProdutoFabricado)
class ProdutoFabricadoAdmin(admin.ModelAdmin):
    inlines = [EstruturaProdutoInline, ItemInstalacaoInline]
    
    list_display = ('codigo_item', 'descricao', 'custo_producao_calculado', 'tempo_de_garantia_meses')
    
    search_fields = ('codigo_item', 'descricao')
    list_per_page = 25
    ordering = ('codigo_item',)
    
    readonly_fields = ('codigo_item', 'custo_producao_calculado',)
    
    fieldsets = (
        ('Dados Gerais', {
            'fields': ('codigo_item', 'descricao', 'unidade_medida')
        }),
        ('Dados de Produção', {
            'fields': ('custo_producao_calculado', 'tempo_de_fabricacao_h', 'tempo_de_garantia_meses')
        }),
    )

@admin.register(EstruturaProduto)
class EstruturaProdutoAdmin(admin.ModelAdmin):
    """
    Visão global de todas as relações da Estrutura de Produto.
    Útil para auditoria e consultas gerais.
    """
    list_display = ('produto_pai', 'componente_filho', 'quantidade')
    search_fields = ('produto_pai__codigo_item', 'componente_filho__codigo_item')
    raw_id_fields = ('produto_pai', 'componente_filho')
    list_per_page = 30

@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade_total', 'quantidade_reserva', 'projeto', 'finalizado')
    search_fields = ('projeto_nome', 'produto__codigo_item')
    list_filter = ('projeto',)
    list_per_page = 20
    ordering = ('-projeto',)

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    inlines = [DemandaInline, AgrupamentoVolumeInline]
    list_display = ('nome', 'status', 'data_inicio', 'data_fim')
    search_fields = ('nome',)
    list_filter = ('status',)
    list_per_page = 20
    ordering = ('-data_inicio',)
    fieldsets = (
        ('Dados Gerais', { 
            'fields': ('nome', 'status', 'data_inicio', 'data_fim')
        }),
    )

    @admin.action(description='🖨️ Gerar Relatorio Instalção (PDF) para o projeto selecionado')
    def gerar_romaneio_action(self, request, queryset):
        
        # 1. VALIDAÇÃO: Garantir que apenas UM projeto foi selecionado
        if queryset.count() != 1:
            self.message_user(request, 
                              "Esta ação só pode ser executada para um projeto de cada vez.", 
                              messages.ERROR)
            return

        # 2. PEGAR O PROJETO
        projeto = queryset.first()

        # 3. PROCESSAR A LÓGICA DO ROMANEIO (Idêntica à view)
        demandas_do_projeto = projeto.demandas.prefetch_related(
            'produto',
            'produto__itens_instalacao',
            'produto__itens_instalacao__item_acessorio'
        )

        lista_romaneio = {}
        for demanda in demandas_do_projeto:
            produto_nome = demanda.produto.descricao
            # A. Adiciona o Produto Principal
            lista_romaneio[produto_nome] = lista_romaneio.get(produto_nome, 0) + demanda.quantidade_total
            
            # B. Adiciona os Itens de Instalação (Kit)
            qtd_para_instalar = demanda.quantidade_instalacao 
            if qtd_para_instalar > 0:
                for item_kit in demanda.produto.itens_instalacao.all():
                    acessorio_nome = item_kit.item_acessorio.descricao
                    qtd_acessorio = item_kit.quantidade * qtd_para_instalar
                    lista_romaneio[acessorio_nome] = lista_romaneio.get(acessorio_nome, 0) + qtd_acessorio

        # 4. GERAR O ARQUIVO PDF (Idêntico à view)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="romaneio_{projeto.nome}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(2*cm, height - 2*cm, f"Romaneio de Carga - Projeto: {projeto.nome}")
        
        y = height - 3.5*cm 
        p.setFont("Helvetica-Bold", 11)
        p.drawString(2*cm, y, "Quantidade")
        p.drawString(6*cm, y, "Descrição do Item")
        p.line(2*cm, y - 0.2*cm, width - 2*cm, y - 0.2*cm)
        y -= 0.7*cm
        
        p.setFont("Helvetica", 10)
        itens_ordenados = sorted(lista_romaneio.items())

        for nome_item, quantidade in itens_ordenados:
            if y < 3*cm:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 2*cm 

            p.drawString(2*cm, y, str(int(quantidade)))
            p.drawString(6*cm, y, nome_item)
            y -= 0.7*cm 

        p.showPage()
        p.save()

        # 5. RETORNAR O PDF
        # Em vez de uma página, a action retorna o arquivo direto
        return response

    @admin.action(description='⚙️ Gerar Ordens de Produção (OPs) para as demandas')
    def gerar_ordens_producao(self, request, queryset):
        
        ops_criadas_count = 0
        demandas_processadas_count = 0
        
        for projeto in queryset:
            demandas = projeto.demandas.all()
            
            for demanda in demandas:
                demandas_processadas_count += 1
                
                op_existente = OrdemProducao.objects.filter(demanda_origem=demanda).exists()
                
                if not op_existente:
                    OrdemProducao.objects.create(
                        produto=demanda.produto,
                        # Use a quantidade_total da demanda
                        quantidade_planejada=demanda.quantidade_total, 
                        projeto=projeto,
                        demanda_origem=demanda,
                        solicitante=request.user, # Bônus: registra quem clicou
                        
                        # AQUI ESTÁ A MUDANÇA:
                        # Usando o TextChoice do seu modelo
                        status=OrdemProducao.StatusOP.PLANEJADA 
                    )
                    ops_criadas_count += 1
        
        if ops_criadas_count > 0:
            self.message_user(request, 
                              f"{ops_criadas_count} novas Ordens de Produção foram criadas.", 
                              messages.SUCCESS)
        else:
            self.message_user(request, 
                              "Nenhuma nova OP precisou ser criada (todas as demandas já tinham OPs).", 
                              messages.WARNING)

    @admin.action(description='🏷️ Gerar Etiquetas de Lote (HTML) para o projeto')
    def gerar_etiquetas_volume(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Selecione apenas UM projeto.", messages.ERROR)
            return

        projeto = queryset.first()
        # Busca todos os LOTES ligados a este projeto
        lotes = projeto.agrupamentos_volume.all().order_by('codigo_lote')

        if not lotes.exists():
            self.message_user(request, "Este projeto não possui lotes de volumes cadastrados.", messages.WARNING)
            return
            
        # --- LÓGICA DO LOOP ---
        # Vamos criar uma lista simples de "etiquetas" para o template
        lista_de_etiquetas_individuais = []
        for lote in lotes:
            # (Ex: lote para "PF-0020", 9 volumes de 16 uni)
            total_volumes_no_lote = lote.numero_de_volumes
            
            # Loop de 1 até 9
            for i in range(1, total_volumes_no_lote + 1):
                etiqueta_data = {
                    "cliente": projeto.nome,
                    "material": lote.produto.descricao,
                    "quantidade": lote.quantidade_por_volume,
                    "codigo_lote": lote.codigo_lote, # Rastreio do Lote
                    "contador_volume": f"Volume: {i} / {total_volumes_no_lote}" # Rastreio da Caixa
                }
                lista_de_etiquetas_individuais.append(etiqueta_data)

        # Seu template HTML, agora modificado para o loop
        html_template_string = """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <title>Impressão de Etiquetas - {{ projeto.nome }}</title>
            <style>
                /* Cole seus estilos completos de etiqueta.html aqui */
                .etiqueta {
                    border: 1px dashed grey; box-sizing: border-box;
                    padding: 10px; overflow: hidden; display: flex;
                    flex-direction: column; justify-content: space-between;
                }
                .etiqueta .header { text-align: center; font-weight: bold; font-size: 0.9em;
                                    border-bottom: 1px solid black; padding-bottom: 5px; margin-bottom: 8px; }
                .etiqueta main { border: 1px solid grey; padding: 8px; margin-bottom: 8px; }
                .etiqueta .item { margin-bottom: 5px; font-size: 0.85em; }
                .etiqueta .item-label { font-weight: bold; }
                .etiqueta .tracking-code { text-align: center; font-weight: bold; font-size: 1.0em;
                                            margin-top: 5px; padding: 3px; border: 1px solid black; }
                
                body { margin: 0; font-family: Arial, sans-serif; background-color: #e0e0e0; }
                .a4-sheet {
                    background: white; width: 210mm; height: 297mm; display: flex;
                    flex-wrap: wrap; align-content: flex-start; margin: 30px auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.5); padding: 5mm; box-sizing: border-box;
                }
                .a4-sheet .etiqueta { width: 97mm; height: 70mm; margin: 1.5mm; }
                @media print {
                    body { background-color: white; }
                    .a4-sheet { margin: 0; box-shadow: none; }
                }
            </style>
        </head>
        <body>
        <div class="a4-sheet">
            
            {% for etiqueta in etiquetas %}
            <div class="etiqueta">
                <div class="header">
                    SMART PICKING SOLUÇÕES DIGITAIS LTDA
                </div>
                <main>
                    <div class="item">
                        <span class="item-label">CLIENTE:</span>
                        <span class="item-value">{{ etiqueta.cliente }}</span>
                    </div>
                    <div class="item">
                        <span class="item-label">MATERIAL:</span>
                        <span class="item-value">{{ etiqueta.material }}</span>
                    </div>
                    <div class="item">
                        <span class="item-label">QUANTIDADE:</span>
                        <span class="item-value">{{ etiqueta.quantidade|floatformat:0 }} PÇS</span>
                    </div>
                </main>
                
                <div class="tracking-code">
                    {{ etiqueta.codigo_lote }} | {{ etiqueta.contador_volume }}
                </div>
            </div>
            {% endfor %}

        </div>
        </body>
        </html>
        """
        
        # Renderiza o template com os dados
        template = Template(html_template_string)
        context = Context({"etiquetas": lista_de_etiquetas_individuais, "projeto": projeto})
        html_renderizado = template.render(context)

        return HttpResponse(html_renderizado)

    # --- E. Registre as actions ---
    actions = [
        'gerar_romaneio_action', 
        'gerar_ordens_producao',
        'gerar_etiquetas_volume', # ❗️❗️ ESTA É A ACTION ATUALIZADA ❗️❗️
    ]