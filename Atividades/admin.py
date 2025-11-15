from django import forms # ❗️ Importação necessária
from django.contrib import admin, messages
from django.utils import timezone
from decimal import Decimal
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, Template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from django.shortcuts import render
from django.utils.html import format_html

# --- Modelos Importados ---
from .models import (
    Volume, ItemVolume, ItemInstalacao, OrdemProducao, Transporte, 
    Fornecedor, Item, MateriaPrima, ProdutoFabricado, EstruturaProduto, 
    Projeto, Demanda, Atividade, OrdemServico, Equipamento, 
    Endereco, Empresa, Transportadora, DefeitoComponente
)

# --- DEFINIÇÕES DE INLINES ---

class ItemVolumeInline(admin.TabularInline):
    model = ItemVolume
    fk_name = 'volume'
    fields = ('produto', 'quantidade')
    extra = 1
    verbose_name_plural = "Conteúdo do Volume (Caixa Mista)"

class ItemInstalacaoInline(admin.TabularInline):
    model = ItemInstalacao
    fk_name = 'produto_pai'
    fields = ('item_acessorio', 'quantidade')
    extra = 1
    verbose_name_plural = "Componentes para Instalação"

class EstruturaProdutoInline(admin.TabularInline):
    model = EstruturaProduto
    fk_name = 'produto_pai'
    fields = ('componente_filho', 'quantidade')
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

@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    """
    Admin completa para Ordens de Produção.
    (Esta secção parecia correta)
    """
    
    @admin.action(description='1. Liberar OPs selecionadas para produção')
    def marcar_como_liberada(self, request, queryset):
        count = 0
        total = queryset.count()
        ops_para_liberar = queryset.filter(status=OrdemProducao.StatusOP.PLANEJADA)
        for op in ops_para_liberar:
            op.liberar_producao() 
            count += 1
        if count > 0:
            self.message_user(request, f"{count} de {total} OPs foram liberadas.", messages.SUCCESS)
        if count < total:
            self.message_user(request, f"{total - count} OPs já estavam em outro status e não foram liberadas.", messages.WARNING)

    @admin.action(description='2. Marcar OPs selecionadas como "Em Produção"')
    def marcar_como_iniciada(self, request, queryset):
        updated_count = queryset.filter(status=OrdemProducao.StatusOP.LIBERADA).update(
            status=OrdemProducao.StatusOP.EM_PRODUCAO,
            data_inicio_real=timezone.now()
        )
        self.message_user(request, f"{updated_count} OPs foram marcadas como 'Em Produção'.", messages.SUCCESS)

    @admin.action(description='3. Concluir OPs selecionadas (Qtd. Produzida = Qtd. Planejada)')
    def marcar_como_concluida(self, request, queryset):
        updated_count = 0
        valid_statuses = [
            OrdemProducao.StatusOP.EM_PRODUCAO, 
            OrdemProducao.StatusOP.CONTROLE_QUALIDADE
        ]
        ops_para_concluir = queryset.filter(status__in=valid_statuses)
        for op in ops_para_concluir:
            op.concluir_producao(quantidade_boa=op.quantidade_planejada) 
            updated_count += 1
        self.message_user(request, f"{updated_count} OPs foram concluídas com sucesso.", messages.SUCCESS)

    @admin.action(description='📋 Gerar Lista de Separação (BOM) para OPs selecionadas')
    def gerar_lista_separacao_producao(self, request, queryset):
        ops_validas = queryset.filter(
            status__in=[
                OrdemProducao.StatusOP.PLANEJADA, 
                OrdemProducao.StatusOP.LIBERADA
            ]
        )
        if not ops_validas.exists():
            self.message_user(request, "Nenhuma OP selecionada é válida (devem ser 'Planejada' ou 'Liberada').", messages.ERROR)
            return

        ops_para_processar = ops_validas.prefetch_related(
            'produto__componentes__componente_filho'
        )
        lista_materiais_agregada = {}
        op_codes = []

        for op in ops_para_processar:
            op_codes.append(op.codigo_op)
            qtd_a_produzir = Decimal(op.quantidade_planejada)
            bom_do_produto = op.produto.componentes.all() 
            
            for componente in bom_do_produto:
                nome_item = componente.componente_filho.descricao
                cod_item = componente.componente_filho.codigo_item
                unidade = componente.componente_filho.get_unidade_medida_display()
                qtd_total_componente = componente.quantidade * qtd_a_produzir
                chave_item = f"({cod_item}) {nome_item}"
                valor_anterior = lista_materiais_agregada.get(chave_item, (Decimal(0), unidade))[0]
                lista_materiais_agregada[chave_item] = (valor_anterior + qtd_total_componente, unidade)

        if not lista_materiais_agregada:
            self.message_user(request, "As OPs selecionadas não possuem uma Lista de Materiais (BOM) definida.", messages.WARNING)
            return

        # Geração do PDF (Lógica de ReportLab)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="lista_separacao_producao.pdf"'
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        p.setFont("Helvetica-Bold", 16)
        p.drawString(2*cm, height - 2*cm, "Lista de Separação para Produção")
        p.setFont("Helvetica", 9)
        p.drawString(2*cm, height - 2.7*cm, f"OPs consolidadas: {', '.join(op_codes)}")
        y = height - 4*cm 
        p.setFont("Helvetica-Bold", 11)
        p.drawString(2*cm, y, "Quantidade")
        p.drawString(5*cm, y, "Unidade")
        p.drawString(8*cm, y, "Item (Código e Descrição)")
        p.line(2*cm, y - 0.2*cm, width - 2*cm, y - 0.2*cm)
        y -= 0.7*cm
        p.setFont("Helvetica", 10)
        itens_ordenados = sorted(lista_materiais_agregada.items())
        for item_nome, (quantidade, unidade) in itens_ordenados:
            if y < 3*cm:
                p.showPage()
                p.setFont("Helvetica", 10)
                y = height - 2*cm 
            p.drawString(2*cm, y, str(quantidade))
            p.drawString(5*cm, y, str(unidade))
            p.drawString(8*cm, y, item_nome)
            y -= 0.7*cm 
        p.showPage()
        p.save()
        return response

    actions = [
        'marcar_como_liberada',
        'marcar_como_iniciada',
        'marcar_como_concluida',
        'gerar_lista_separacao_producao',
    ]

    # Configurações de layout (corrigidas)
    list_display = ('codigo_op', 'status', 'produto', 'quantidade_planejada', 'data_prevista_conclusao', 'data_emissao')
    list_filter = ('status', 'data_prevista_conclusao', 'data_emissao', 'produto', 'projeto')
    search_fields = ('codigo_op', 'produto__codigo_item', 'produto__descricao', 'projeto__nome')
    readonly_fields = ('codigo_op', 'data_emissao', 'data_conclusao_real', 'quantidade_produzida', 'custo_estimado', 'custo_real')
    fieldsets = (
        ('Informações Principais', {'fields': ('codigo_op', 'status', 'produto', 'quantidade_planejada')}),
        ('Custos (Calculados)', {'fields': ('custo_estimado', 'custo_real')}),
        ('Datas', {'fields': ('data_emissao', 'data_prevista_conclusao', 'data_inicio_real', 'data_conclusao_real')}),
        ('Contexto e Responsáveis', {'fields': ('solicitante', 'projeto', 'demanda_origem')}),
        ('Resultados e Observações', {'fields': ('quantidade_produzida', 'observacoes')}),
    )

# --- OUTROS ADMINS (simplificados para clareza) ---

@admin.register(Transportadora)
class TransportadoraoAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'nome_contato', 'telefone', 'observacoes')

@admin.register(Transporte)
class TransporteAdmin(admin.ModelAdmin):
    pass

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('solicitante', 'local_execucao', 'nota_entrada', 'nota_saida', 'projeto' , 'transporte')

@admin.register(DefeitoComponente)
class DefeitoComponenteAdmin(admin.ModelAdmin):
    list_display = ('componente', 'defeito', 'efeito', 'causa')

@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    list_display = ('id_empresa', 'apelido_endereco', 'cidade', 'uf')

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['razao_social', 'cnpj', 'data_cadastro']

@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ('tipo_atividade', 'data_inicial', 'data_final', 'responsavel', 'projeto', 'status')
    search_fields = ('responsavel__username', 'projeto__nome')
    list_filter = ('tipo_atividade', 'status', 'data_inicial', 'data_final')

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'numero_serie', 'projeto_alocado')
    search_fields = ('produto__codigo_item', 'numero_serie', 'projeto_alocado__nome')
    list_filter = ('projeto_alocado',)

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj')
    search_fields = ('razao_social', 'cnpj')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('codigo_item', 'descricao', 'unidade_medida', 'tipo_especifico')
    list_display_links = ('codigo_item', 'descricao')
    list_filter = ('unidade_medida',)
    search_fields = ('codigo_item', 'descricao')
    ordering = ('codigo_item',)
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display = ('codigo_item', 'descricao', 'preco_custo_compra', 'fornecedor_padrao')
    search_fields = ('codigo_item', 'descricao', 'fornecedor_padrao__razao_social')
    list_filter = ('fornecedor_padrao',)
    ordering = ('codigo_item',)
    readonly_fields = ('codigo_item',)
    fieldsets = (
        ('Dados Gerais (Herdado de Item)', {'fields': ('codigo_item', 'descricao', 'unidade_medida')}),
        ('Dados de Compra', {'fields': ('preco_custo_compra', 'fornecedor_padrao')}),
    )

@admin.register(ProdutoFabricado)
class ProdutoFabricadoAdmin(admin.ModelAdmin):
    inlines = [EstruturaProdutoInline, ItemInstalacaoInline]
    list_display = ('codigo_item', 'descricao', 'custo_producao_calculado', 'tempo_de_garantia_meses')
    search_fields = ('codigo_item', 'descricao')
    ordering = ('codigo_item',)
    readonly_fields = ('codigo_item', 'custo_producao_calculado',)
    fieldsets = (
        ('Dados Gerais', {'fields': ('codigo_item', 'descricao', 'unidade_medida')}),
        ('Dados de Produção', {'fields': ('custo_producao_calculado', 'tempo_de_fabricacao_h', 'tempo_de_garantia_meses')}),
    )

@admin.register(EstruturaProduto)
class EstruturaProdutoAdmin(admin.ModelAdmin):
    list_display = ('produto_pai', 'componente_filho', 'quantidade')
    search_fields = ('produto_pai__codigo_item', 'componente_filho__codigo_item')

@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade_total', 'quantidade_reserva', 'projeto', 'finalizado')
    search_fields = ('projeto_nome', 'produto__codigo_item')
    list_filter = ('projeto',)
    ordering = ('-projeto',)

# --- ADMIN DO PROJETO (CORRIGIDO) ---

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    # <-- CORREÇÃO: Adicionámos os inlines corretos -->
    inlines = [DemandaInline] 
    
    list_display = ('nome', 'status', 'data_inicio', 'data_fim')
    search_fields = ('nome',)
    list_filter = ('status',)
    ordering = ('-data_inicio',)
    fieldsets = (
        ('Dados Gerais', { 
            'fields': ('nome', 'status', 'data_inicio', 'data_fim')
        }),
    )

    @admin.action(description='🖨️ Gerar Relatorio Instalção (PDF) para o projeto selecionado')
    def gerar_romaneio_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Esta ação só pode ser executada para um projeto de cada vez.", messages.ERROR)
            return

        projeto = queryset.first()
        demandas_do_projeto = projeto.demandas.prefetch_related(
            'produto',
            'produto__itens_instalacao',
            'produto__itens_instalacao__item_acessorio'
        )

        lista_romaneio = {}
        for demanda in demandas_do_projeto:
            produto_nome = demanda.produto.descricao
            lista_romaneio[produto_nome] = lista_romaneio.get(produto_nome, 0) + demanda.quantidade_total
            
            qtd_para_instalar = demanda.quantidade_instalacao 
            if qtd_para_instalar > 0:
                for item_kit in demanda.produto.itens_instalacao.all():
                    acessorio_nome = item_kit.item_acessorio.descricao
                    qtd_acessorio = item_kit.quantidade * qtd_para_instalar
                    lista_romaneio[acessorio_nome] = lista_romaneio.get(acessorio_nome, 0) + qtd_acessorio

        # Geração do PDF (Lógica de ReportLab)
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
                        quantidade_planejada=demanda.quantidade_total, 
                        projeto=projeto,
                        demanda_origem=demanda,
                        solicitante=request.user, 
                        status=OrdemProducao.StatusOP.PLANEJADA 
                    )
                    ops_criadas_count += 1
        
        if ops_criadas_count > 0:
            self.message_user(request, f"{ops_criadas_count} novas Ordens de Produção foram criadas.", messages.SUCCESS)
        else:
            self.message_user(request, "Nenhuma nova OP precisou ser criada (todas as demandas já tinham OPs).", messages.WARNING)

    # <-- CORREÇÃO: Lógica de etiquetas removida daqui -->
    # <-- CORREÇÃO: 'actions' atualizadas -->
    actions = [
        'gerar_romaneio_action', 
        'gerar_ordens_producao',
    ]



# Em seu_app/admin.py
# (Logo antes da sua classe VolumeAdmin)

class CloneForm(forms.Form):
    """
    Este é o formulário que vai aparecer no "popup".
    """
    copias_a_criar = forms.IntegerField(
        label='Número de cópias para CADA volume selecionado',
        min_value=1,
        initial=1,
        
        # ❗️ AQUI ESTÁ A MUDANÇA ❗️
        # Adicionamos 'class': 'form-control'
        widget=forms.NumberInput(attrs={
            'autofocus': 'autofocus',
            'class': 'form-control' 
        })
    )
# Em seu_app/admin.py

# ... (outros admins, como ProjetoAdmin) ...

#
# --- C. A CLASSE 'VolumeAdmin' FINAL E CORRIGIDA ---
#
@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    """
    VERSÃO FINAL:
    - Com a Action de "popup" (que vai funcionar).
    - COM A COLUNA DE CONTEÚDO (que faltava).
    """
    model = Volume
    inlines = [ItemVolumeInline]
    
    # ❗️ O 'mostrar_conteudo' agora vai funcionar
    list_display = ('codigo_volume', 'projeto', 'mostrar_conteudo', 'data_embalado')
    
    list_filter = ('data_embalado', 'projeto')
    search_fields = ('codigo_volume', 'projeto__nome')
    
    # 1. A ACTION DE ETIQUETA (Permanece)
    @admin.action(description='🏷️ Gerar Etiqueta(s) de Volume (HTML)')
    def gerar_etiqueta_volume_action(self, request, queryset):
        
        volumes = queryset.prefetch_related(
            'itens_dentro__produto', 
            'projeto'
        )
        
        # O seu template HTML (fica igual)
        html_template_string = """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head><title>Impressão de Etiquetas</title>
        <style>
            /* ... Seu CSS completo da etiqueta ... */
            .etiqueta {
                border: 1px dashed grey; box-sizing: border-box;
                padding: 10px; overflow: hidden; display: flex;
                flex-direction: column; justify-content: space-between;
                width: 97mm; height: 70mm; margin: 1.5mm;
            }
            .etiqueta .header { text-align: center; font-weight: bold; font-size: 0.9em;
                                border-bottom: 1px solid black; padding-bottom: 5px; margin-bottom: 8px; }
            .etiqueta main { border: 1px solid grey; padding: 8px; margin-bottom: 8px; }
            .etiqueta .item { margin-bottom: 5px; font-size: 0.8em; }
            .etiqueta .item-label { font-weight: bold; }
            .etiqueta .tracking-code { text-align: center; font-weight: bold; font-size: 1.1em;
                                        margin-top: 5px; padding: 5px; border: 1px solid black; }
            body { margin: 0; font-family: Arial, sans-serif; background-color: #e0e0e0; }
            .a4-sheet {
                background: white; width: 210mm; height: 297mm; display: flex;
                flex-wrap: wrap; align-content: flex-start; margin: 30px auto;
                box-shadow: 0 0 10px rgba(0,0,0,0.5); padding: 5mm; box-sizing: border-box;
            }
            @media print {
                body { background-color: white; }
                .a4-sheet { margin: 0; box-shadow: none; }
            }
        </style>
        </head>
        <body>
        <div class="a4-sheet">
            {% for volume in volumes %}
            <div class="etiqueta">
                <div class="header">SMART PICKING...</div>
                <main>
                    <div class="item">
                        <span class="item-label">CLIENTE:</span>
                        <span class="item-value">{{ volume.projeto.nome }}</span>
                    </div>
                    {% for item in volume.itens_dentro.all %}
                    <div class="item">
                        <span class="item-label">{{ item.quantidade|floatformat:0 }}x</span>
                        <span class="item-value">{{ item.produto.descricao }}</span>
                    </div>
                    {% endfor %}
                </main>
                <div class="tracking-code">{{ volume.codigo_volume }}</div>
            </div>
            {% endfor %}
        </div>
        </body>
        </html>
        """
        
        template = Template(html_template_string)
        context = Context({"volumes": volumes})
        html_renderizado = template.render(context)

        return HttpResponse(html_renderizado)

    # 2. A NOVA ACTION DE "CLONAR"
    @admin.action(description='🔄 Clonar Volume(s) selecionado(s)...')
    def clonar_volumes_action(self, request, queryset):
        
        # --- ETAPA 2: O 'popup' (página intermédia) FOI SUBMETIDO ---
        if 'apply' in request.POST:
            form = CloneForm(request.POST)
            
            if form.is_valid():
                copias = form.cleaned_data['copias_a_criar']
                
                clones_criados = 0
                # O 'queryset' aqui são os volumes que o utilizador selecionou
                for volume_original in queryset:
                    itens_originais = list(volume_original.itens_dentro.all())
                    
                    for i in range(copias):
                        # a. Cria o clone do 'Pai' (Volume)
                        novo_volume = Volume.objects.create(
                            projeto=volume_original.projeto,
                            data_embalado=volume_original.data_embalado
                        )
                        # b. Copia os 'Filhos' (ItemVolume)
                        novos_itens = [
                            ItemVolume(
                                volume=novo_volume,
                                produto=item.produto,
                                quantidade=item.quantidade
                            ) for item in itens_originais
                        ]
                        ItemVolume.objects.bulk_create(novos_itens)
                        clones_criados += 1

                self.message_user(request, f"{clones_criados} clones criados com sucesso.", messages.SUCCESS)
                return HttpResponseRedirect(request.get_full_path())
            
            # Se o formulário for inválido, apenas volta
            else:
                self.message_user(request, "Por favor, insira um número válido.", messages.ERROR)
                return HttpResponseRedirect(request.get_full_path())

        # --- ETAPA 1: O utilizador ACABOU de clicar na action ---
        else:
            form = CloneForm()
            
            # ❗️❗️ A ALTERAÇÃO ESTÁ AQUI ❗️❗️
            # Nós otimizamos a 'queryset' ANTES de a enviar para o template,
            # pré-buscando o conteúdo de cada volume.
            volumes_a_clonar = queryset.prefetch_related('itens_dentro__produto', 'projeto')
            
            context = {
                'title': 'Clonar Volumes',
                'form': form,
                # Passamos a queryset otimizada
                'volumes_selecionados': volumes_a_clonar, 
                'action_checkbox_name':  "_selected_action",
            }
            # Renderiza o template que vamos criar
            return render(request, 'admin/clonar_volumes_intermediate.html', context)
    # 3. REGISTRE AS DUAS ACTIONS
    actions = ['gerar_etiqueta_volume_action', 'clonar_volumes_action']
    
    # 
    # ❗️ 4. OS MÉTODOS EM FALTA (ADICIONADOS AQUI) ❗️
    #
    @admin.display(description='Conteúdo do Volume')
    def mostrar_conteudo(self, obj):
        """
        Cria o HTML para a coluna 'Conteúdo'.
        """
        # 'itens_dentro' foi otimizado pelo 'get_queryset' abaixo
        itens = obj.itens_dentro.all()
        
        if not itens:
            return "--- Vazio ---"
        
        item_strings = [
            f"<b>{int(item.quantidade)}x</b> {item.produto.descricao}"
            for item in itens
        ]
        
        return format_html("<br>".join(item_strings))

    def get_queryset(self, request):
        """
        Otimiza a página, evitando o "N+1 query problem".
        """
        qs = super().get_queryset(request)
        # Otimiza, "pré-buscando" os itens filhos e o produto de cada item
        return qs.prefetch_related('itens_dentro__produto')