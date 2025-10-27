from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone

class Fornecedor(models.Model):
    razao_social = models.CharField(max_length=200, unique=True)
    cnpj = models.CharField(max_length=18, unique=True) # 14 digitos + pontuação

    def __str__(self):
        return self.razao_social

class Item(models.Model):
    UNIDADES_CHOICES = [
        ('UN', 'Unidade'),
        ('M', 'Metro'),
        ('CM', 'Centímetro'),
        ('KG', 'Quilograma'),
        ('L', 'Litro'),
    ]

    codigo_item = models.CharField(max_length=50, unique=True, help_text="Código único do item (SKU)")
    descricao = models.CharField(max_length=255)
    unidade_medida = models.CharField(max_length=3, choices=UNIDADES_CHOICES, default='UN')

    def __str__(self):
        return f"{self.codigo_item or '[NOVO]'} - {self.descricao}"

    @property
    def tipo_especifico(self):
        """
        Determina o prefixo do SKU com base no tipo real do objeto.
        Esta é a versão corrigida usando isinstance().
        """
        if isinstance(self, MateriaPrima):
            return 'MP'
        if isinstance(self, ProdutoFabricado):
            return 'PF'
        return 'GEN'

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para gerar o SKU automaticamente na criação.
        """
        if self.pk is None and not self.codigo_item:
            prefix = self.tipo_especifico
            
            with transaction.atomic():
                last_item = Item.objects.select_for_update().filter(
                    codigo_item__startswith=f"{prefix}-"
                ).order_by('codigo_item').last()
                
                if last_item:
                    last_number_str = last_item.codigo_item.split('-')[-1]
                    new_number = int(last_number_str) + 1
                else:
                    new_number = 1
                
                self.codigo_item = f"{prefix}-{str(new_number).zfill(4)}"
        
        super().save(*args, **kwargs)

class MateriaPrima(Item):
    preco_custo_compra = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0.00,
        help_text="Custo de aquisição do item do fornecedor."
    )
    fornecedor_padrao = models.ForeignKey(
        Fornecedor, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        verbose_name = "Matéria-Prima"
        verbose_name_plural = "Matérias-Primas"

class ProdutoFabricado(Item):
    custo_producao_calculado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Custo calculado com base na estrutura de produto (BOM)."
    )
    tempo_de_fabricacao_h = models.FloatField(
        default=0,
        help_text="Tempo estimado de fabricação em horas."
    )
    tempo_de_garantia_meses = models.PositiveIntegerField(
        default=0,
        help_text="Tempo de garantia em meses para o cliente final."
    )

    class Meta:
        verbose_name = "Produto Fabricado"
        verbose_name_plural = "Produtos Fabricados"

class EstruturaProduto(models.Model):
    produto_pai = models.ForeignKey(
        ProdutoFabricado, 
        on_delete=models.CASCADE, 
        related_name='componentes'
    )
    componente_filho = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE, 
        related_name='usado_em'
    )
    quantidade = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.quantidade} x {self.componente_filho.codigo_item} para montar {self.produto_pai.codigo_item}"

    class Meta:
        unique_together = ('produto_pai', 'componente_filho') # Garante que um componente só seja adicionado uma vez por produto

class Projeto(models.Model):
    status_choices = [
        ('NI', 'Não Iniciado'),
        ('IM', 'Implantação'),
        ('FN', 'Finalizado'),
        ('EN', 'Enviado'),
        ('PR', 'Produção'),
        ('AG', 'Aguardando GOLIVE'),
        ('GO', 'GOLIVE'),
    ]
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True)
    status = models.CharField(choices=status_choices, default='NI', max_length=2)
    data_inicio = models.DateTimeField(null=True, blank=True)
    data_fim = models.DateTimeField(null=True, blank=True)

    def get_status_badge_class(self):
        """Retorna a classe CSS do Bootstrap para o status atual."""
        if self.status == 'FN':
            return 'bg-success'
        elif self.status in ['IM', 'EN', 'PR', 'GO']:
            return 'bg-primary'
        elif self.status == 'AG':
            return 'bg-warning text-dark'
        else:
            return 'bg-secondary'

    def __str__(self):
        return self.nome

class Demanda(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    quantidade = models.IntegerField()
    produto = models.ForeignKey(Item, on_delete=models.CASCADE)
    finalizado = models.BooleanField(default=False)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE,  related_name='demandas')

    def __str__(self):
        value = int(self.quantidade)
        desc = self.nome if self.nome else self.produto.descricao
        return f"{value} x {desc}"

class Equipamento(models.Model):
    """
    Representa um item físico, único e rastreável.
    """
    produto = models.ForeignKey(ProdutoFabricado, on_delete=models.PROTECT)
    numero_serie = models.CharField(max_length=100, unique=True, db_index=True)
    projeto_alocado = models.ForeignKey(Projeto, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.produto.descricao} (S/N: {self.numero_serie})"

class Atividade(models.Model):
    atividade_choices = [
        ('M', 'MONTAGEM'),
        ('E', 'EMBALAGEM'),
        ('MA', 'MANUTENÇÃO'),
    ]
    situacao_choices = [
        ('P', 'PENDENTE'),
        ('C', 'FINALIZADA'),
    ]

    dataInicial = models.DateTimeField()
    dataFinal = models.DateTimeField(null=True, blank=True)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    tipoAtividade = models.CharField(choices=atividade_choices, max_length=2)
    situacao = models.CharField(choices=situacao_choices, max_length=1, default='P')
    observacoes = models.TextField(blank=True)
    excluido = models.BooleanField(default=False)

    equipamentos = models.ManyToManyField(
        Equipamento,
        blank=True, 
        related_name='atividades' 
    )

    def __str__(self):
        return f"{self.get_tipoAtividade_display()} - {self.projeto.nome}"

class DefeitoComponente(models.Model):
    componente = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='registro_defeitos')
    defeito = models.CharField(max_length=255)
    efeito = models.CharField(max_length=255, blank=True)
    causa = models.CharField(max_length=255, blank=True)
        
class Empresa(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name='Razão social')
    nome_fantasia = models.CharField(max_length=150, verbose_name='Nome Fantasia')
    cnpj = models.CharField(max_length=18, unique=True, verbose_name="CNPJ")
    inscricao_statual = models.CharField(max_length=20, null=True, blank=True, verbose_name='Inscrição Estadual(IE)', help_text="Obrigatório para emissão de NF-e de produto.")
    data_cadastro = models.DateTimeField(verbose_name="Data de Cadastro", default=timezone.now, editable=False)

    class Meta:
        ordering = ['nome_fantasia', 'razao_social']
    
    def __str__(self):
        """
        Retorna o nome da empresa em formato Title Case.
        Dá preferência ao Nome Fantasia; se não houver, usa a Razão Social.
        """
        nome_para_exibir = self.nome_fantasia if self.nome_fantasia else self.razao_social
        return (nome_para_exibir or "").title()
    

class Endereco(models.Model):
    id_empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="enderecos", verbose_name="Empresa")
    apelido_endereco = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9, verbose_name='CEP')
    numero = models.CharField(max_length=20, verbose_name='Número')
    complemento = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    uf = models.CharField(max_length=2, verbose_name='UF')
    
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
        
    def __str__(self):
        if self.apelido_endereco:
            return f"{self.apelido_endereco}({self.id_empresa.nome_fantasia})"
        return f"{self.numero} - {self.cidade}({self.id_empresa.nome_fantasia})"

class Transportadora(models.Model):
    razao_social = models.CharField(max_length=255, verbose_name='Razão social')
    nome_contato =  models.CharField(max_length=100, verbose_name='Nome para Contato', blank=True)
    telefone = models.CharField(blank=True, max_length=20)
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.razao_social}"

class OrdemProducao(models.Model):
    pass

class OrdemCompra(models.Model):
    pass

class Transporte(models.Model):
    remetente = models.ForeignKey(
        Endereco,
        on_delete=models.PROTECT,
        related_name="envios_como_remetente",
        verbose_name="Remetente"
    )
    destinatario = models.ForeignKey(
        Endereco,
        on_delete=models.PROTECT,
        related_name="envios_como_destinatario",
        verbose_name="Destinatário"
    )

    aos_cuidados = models.CharField(max_length=100, verbose_name="A/C (Aos Cuidados de)", blank=True)
    
    def __str__(self):
        return f"{self.destinatario}"

class OrdemServico(models.Model):
    solicitante = models.ForeignKey(Empresa, on_delete=models.PROTECT)
    local_execucao = models.ForeignKey(Endereco, on_delete=models.PROTECT)
    data_inicio = models.DateTimeField(default=timezone.now, editable=False)
    dataTermino = models.DateTimeField(blank=True, null=True)
    nota_entrada = models.CharField(max_length=50,blank=True, null=True)
    nota_saida = models.CharField(max_length=50,blank=True, null=True)
    tecnico_responsavel = models.ManyToManyField(User, related_name='ordem_serivico')
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='ordens_servico')
    transporte = models.ForeignKey(Transporte, on_delete=models.PROTECT)
    transportadora_padrao = models.ForeignKey(Transportadora, on_delete=models.PROTECT ,verbose_name="Transportadora_Padrão")
    codigo_rastreio = models.CharField(max_length=50, verbose_name="Cód. Rastreio", blank=True)

class ServicoRealizado(models.Model):
    acao_choices = (
        ('T', 'TROCAR'),
        ('M', 'MANUTENÇÃO'),
        ('J', 'JUMPER'),
        ('R', 'RESOLDAR')
    )
    acao = models.CharField(choices=acao_choices, max_length=1)
    componente = models.ForeignKey(Item, on_delete=models.PROTECT)
    obeservacao = models.TextField()

class DefeitoEquipamento(models.Model):
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.PROTECT)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.PROTECT, related_name='historico_defeitos')
    falha = models.ForeignKey(DefeitoComponente, on_delete=models.PROTECT, related_name='defeitos_equipamentos')
    acao_necessaria = models.ForeignKey(ServicoRealizado, on_delete=models.PROTECT)
    data_identificacao = models.DateTimeField(default=timezone.now, editable=False, verbose_name='Data Identificado')
    
    class Meta:
        ordering = ['equipamento']