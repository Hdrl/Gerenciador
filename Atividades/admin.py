from django.contrib import admin
from .models import OrdemProducao, Transporte ,Fornecedor, Item, MateriaPrima, ProdutoFabricado, EstruturaProduto, Projeto, Demanda, Atividade, OrdemServico, Equipamento, Endereco, Empresa, Transportadora, DefeitoComponente

from django.contrib import admin, messages
from django.utils import timezone
from .models import OrdemProducao 
# Importe também seus outros modelos se precisar deles para Inlines
# ex: from produtos.models import ProdutoFabricado

@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    """
    Configuração personalizada do Admin para Ordens de Produção.
    """

    # --- AÇÕES CUSTOMIZADAS (O mais importante!) ---
    # Permite que você execute a lógica de negócio da sua OP
    # diretamente da lista do admin.
    
    @admin.action(description='1. Liberar OPs selecionadas para produção')
    def marcar_como_liberada(self, request, queryset):
        """
        Executa a ação de 'liberar_producao' do modelo.
        """
        count = 0
        total = queryset.count()
        
        # Filtra apenas as que podem ser liberadas
        ops_para_liberar = queryset.filter(status=OrdemProducao.StatusOP.PLANEJADA)
        
        for op in ops_para_liberar:
            op.liberar_producao()  # Chama o método do seu modelo
            count += 1
            
        if count > 0:
            self.message_user(request, f"{count} de {total} OPs foram liberadas.", messages.SUCCESS)
        if count < total:
            self.message_user(request, f"{total - count} OPs já estavam em outro status e não foram liberadas.", messages.WARNING)

    @admin.action(description='2. Marcar OPs selecionadas como "Em Produção"')
    def marcar_como_iniciada(self, request, queryset):
        """
        Inicia a produção das OPs que estão 'LIBERADA'.
        """
        updated_count = queryset.filter(status=OrdemProducao.StatusOP.LIBERADA).update(
            status=OrdemProducao.StatusOP.EM_PRODUCAO,
            data_inicio_real=timezone.now()
        )
        self.message_user(request, f"{updated_count} OPs foram marcadas como 'Em Produção'.", messages.SUCCESS)

    @admin.action(description='3. Concluir OPs selecionadas (Qtd. Produzida = Qtd. Planejada)')
    def marcar_como_concluida(self, request, queryset):
        """
        Ação de conclusão rápida. Assume que a Qtd. Produzida é igual à Planejada.
        """
        updated_count = 0
        valid_statuses = [
            OrdemProducao.StatusOP.EM_PRODUCAO, 
            OrdemProducao.StatusOP.CONTROLE_QUALIDADE
        ]
        
        ops_para_concluir = queryset.filter(status__in=valid_statuses)

        for op in ops_para_concluir:
            op.status = OrdemProducao.StatusOP.CONCLUIDA
            op.data_conclusao_real = timezone.now()
            op.quantidade_produzida = op.quantidade_planejada  # Suposição da ação
            op.save()
            updated_count += 1
            
        self.message_user(request, f"{updated_count} OPs foram concluídas com sucesso.", messages.SUCCESS)

    # --- Configuração da Lista de Exibição ---
    list_display = (
        'codigo_op',
        'status',
        'produto',
        'quantidade_planejada',
        'data_prevista_conclusao',
        'data_emissao',
        'solicitante',
    )
    
    # --- Filtros (essencial para PCP) ---
    list_filter = (
        'status',
        'data_prevista_conclusao',
        'data_emissao',
        'produto',
        'solicitante',
        'projeto',
    )
    
    # --- Barra de Pesquisa ---
    search_fields = (
        'codigo_op',
        'produto__codigo',  # Assumindo que seu modelo Produto tem um campo 'codigo'
        'produto__descricao', # Assumindo que seu modelo Produto tem 'descricao'
        'solicitante__username',
        'projeto__nome', # Assumindo que seu modelo Projeto tem 'nome'
    )
    
    # --- Campos que não podem ser editados manualmente ---
    # O código OP e datas de log são controlados pelo sistema
    readonly_fields = (
        'codigo_op',
        'data_emissao',
        'data_inicio_real',
        'data_conclusao_real',
        'quantidade_produzida', # Deve ser atualizado por uma ação ou na conclusão
    )

    # --- Organização do Formulário de Edição ---
    # Divide o formulário em seções lógicas
    fieldsets = (
        ('Informações Principais', {
            'fields': (
                'codigo_op',
                'status',
                'produto',
                'quantidade_planejada',
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
            )
        }),
        ('Resultados e Observações', {
            'fields': (
                'quantidade_produzida',
                'observacoes',
            )
        }),
    )

    # --- Adiciona as Ações ao Admin ---
    actions = [
        'marcar_como_liberada',
        'marcar_como_iniciada',
        'marcar_como_concluida',
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
    list_display = ('tipoAtividade', 'dataInicial', 'dataFinal', 'responsavel', 'projeto', 'situacao')
    search_fields = ('responsavel__username', 'projeto__nome')
    list_filter = ('tipoAtividade', 'situacao', 'dataInicial', 'dataFinal')
    list_per_page = 20

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('produto', 'numero_serie', 'projeto_alocado')
    search_fields = ('produto__codigo_item', 'numero_serie', 'projeto_alocado__nome')
    list_filter = ('projeto_alocado',)
    list_per_page = 20  

@admin.register(Demanda)
class DemandaAdmin(admin.ModelAdmin):
    list_display = ('produto', 'quantidade', 'projeto', 'finalizado')
    search_fields = ('projeto_nome', 'produto__codigo_item')
    list_filter = ('projeto',)
    list_per_page = 20
    ordering = ('-projeto',)

@admin.register(Projeto)
class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'data_inicio', 'data_fim')
    search_fields = ('nome',)
    list_filter = ('status',)
    list_per_page = 20
    ordering = ('-data_inicio',)
    
# 1. Configuração para o modelo Fornecedor
@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    """
    Admin para o cadastro de Fornecedores.
    """
    list_display = ('razao_social', 'cnpj')
    search_fields = ('razao_social', 'cnpj')
    list_per_page = 20


# 2. Configuração da Estrutura de Produto (BOM) como um "Inline"
class EstruturaProdutoInline(admin.TabularInline):
    """
    Permite editar os componentes (BOM) diretamente na página do Produto Fabricado.
    'TabularInline' é mais compacto e ideal para listas de componentes.
    """
    model = EstruturaProduto
    # 'fk_name' especifica qual chave estrangeira no modelo 'EstruturaProduto'
    # se refere ao modelo pai (ProdutoFabricado).
    fk_name = 'produto_pai'
    
    # Campos que aparecerão na linha de edição do componente.
    fields = ('componente_filho', 'quantidade')
    
    # Para catálogos grandes, 'raw_id_fields' substitui o dropdown de seleção
    # por um campo de busca com lupa, muito mais performático e usável.
    raw_id_fields = ('componente_filho',)
    
    # Quantidade de linhas extras para adicionar novos componentes.
    extra = 1
    verbose_name = "Componente da Estrutura"
    verbose_name_plural = "Componentes da Estrutura (Bill of Materials)"


# 3. Configuração para o modelo base Item
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


# 4. Configuração para o modelo MateriaPrima
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
    inlines = [EstruturaProdutoInline]
    
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

# Opcional: Registrar EstruturaProduto para ter uma visão global, se desejado.
# Geralmente, a edição pelo inline é suficiente.
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