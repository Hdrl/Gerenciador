from django.contrib import admin
from .models import Fornecedor, Item, MateriaPrima, ProdutoFabricado, EstruturaProduto, Projeto, Demanda, Atividade, OrdemServico, Equipamento

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ('solicitante', 'localExecucao', 'Transportadora', 'projeto', 'dataInicio', 'dataTermino')
    search_fields = ('solicitante', 'Transportadora', 'projeto__nome')
    list_filter = ('localExecucao', 'dataInicio', 'dataTermino')
    list_per_page = 20
    ordering = ('-dataInicio',)

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