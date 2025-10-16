from django.db import models, transaction
from django.contrib.auth.models import User

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
    status = models.CharField(choices=status_choices, default='N', max_length=2)
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
        desc = self.descricao if self.descricao else self.produto.descricao
        return f"{value} x {desc}"

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
    dataFinal = models.DateTimeField()
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    tipoAtividade = models.CharField(choices=atividade_choices, max_length=2)
    situacao = models.CharField(choices=situacao_choices, max_length=1)

class produtoFabricadoAtividade(models.Model):
    atividade = models.ForeignKey(Atividade, on_delete=models.CASCADE)
    produtoFabricado = models.ForeignKey(ProdutoFabricado, on_delete=models.CASCADE)
    quantidade = models.DecimalField(max_digits=10, decimal_places=4)

class Problema(models.Model):
    idProblema = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=100)

class OrdemServico(models.Model):
    localExecucao_choices = [
        ('E', 'Empresa'),
        ('C', 'Cliente'),
    ]
    solicitante = models.CharField(max_length=100)
    localExecucao = models.CharField(choices=localExecucao_choices, max_length=1)
    Transportadora = models.CharField(max_length=100)
    codigoRastreio = models.CharField(max_length=100, null=True)
    dataInicio = models.DateTimeField()
    dataTermino = models.DateTimeField(null=True)
    NFEntrada = models.CharField(max_length=50, null=True)
    NFSaida = models.CharField(max_length=50, null=True)
    defeitoInformado = models.TextField()
    diagnosticoTecnico = models.TextField(null=True)
    servicoRealizado = models.TextField(null=True)
    tecnicoResponsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name='ordens_servico')