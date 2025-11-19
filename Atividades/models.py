from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

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
        tipo = ContentType.objects.get_for_model(self).model
        return {
            'materiaprima': 'MP',
            'produtofabricado': 'PF'
        }.get(tipo, 'GEN')

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
        editable=False,
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
    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'

    def __str__(self):
        return self.nome

class Demanda(models.Model):
    nome = models.CharField(max_length=200, null=True, blank=True)
    quantidade_total = models.IntegerField("Qtd. Total")
    quantidade_reserva = models.IntegerField("Qtd. Reserva", default=0, blank=True)
    produto = models.ForeignKey(ProdutoFabricado, on_delete=models.CASCADE)
    finalizado = models.BooleanField(default=False)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE,  related_name='demandas')

    @property
    def quantidade_instalacao(self):
        """
        Propriedade calculada que nos diz quantos 
        itens realmente precisam de um kit.
        """
        return self.quantidade_total - self.quantidade_reserva
    
    def __str__(self):
        value = int(self.quantidade_total)
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
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        FINALIZADO = 'FINALIZADO', 'Finalizado'

    data_inicial = models.DateTimeField(editable=False, default=timezone.now)
    data_final = models.DateTimeField(null=True, blank=True, editable=False)
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    tipo_atividade = models.CharField(choices=atividade_choices, max_length=2)
    status = models.CharField(choices=Status.choices, max_length=20, default=Status.PENDENTE)
    observacoes = models.TextField(blank=True)
    excluido = models.BooleanField(default=False)

    equipamentos = models.ManyToManyField(
        Equipamento,
        blank=True, 
        related_name='atividades' 
    )

    def __str__(self):
        return f"{self.get_tipo_atividade_display()} - {self.projeto.nome}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            try:
                original =  self.__class__.objects.get(pk=self.pk)
                if (original.status == self.Status.PENDENTE and  self.status == self.Status.FINALIZADO and self.data_final is None):
                    self.data_final = timezone.now()
            except ObjectDoesNotExist:
                pass
        else:
            if self.status == self.Status.FINALIZADO and self.data_final is None:
                self.data_final = timezone.now()
        super().save(*args, **kwargs)

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
    """
    A Ordem de Produção (OP) é o documento principal para
    iniciar o processo de fabricação. (VERSÃO COMBINADA)
    """
    class StatusOP(models.TextChoices):
        PLANEJADA = 'PLANEJADA', 'Planejada'
        LIBERADA = 'LIBERADA', 'Liberada para Produção'
        EM_PRODUCAO = 'EM_PRODUCAO', 'Em Produção'
        CONTROLE_QUALIDADE = 'QUALIDADE', 'Controle de Qualidade'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        CANCELADA = 'CANCELADA', 'Cancelada'

    produto = models.ForeignKey(
        ProdutoFabricado, 
        on_delete=models.PROTECT, 
        related_name='ordens_producao',
        help_text="O produto final que será fabricado"
    )
    quantidade_planejada = models.PositiveIntegerField(
        help_text="Quantidade que deve ser produzida"
    )
    codigo_op = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        help_text="Código único da Ordem (ex: OP-00123)"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusOP.choices,
        default=StatusOP.PLANEJADA,
        db_index=True 
    )
    data_emissao = models.DateTimeField(
        default=timezone.now,
        help_text="Data em que a OP foi criada no sistema"
    )
    data_prevista_conclusao = models.DateField(
        help_text="Data limite para a conclusão da produção",
        blank=True,
        null=True
    )
    data_inicio_real = models.DateTimeField(
        null=True, blank=True,
        help_text="Data e hora que a produção realmente começou"
    )
    data_conclusao_real = models.DateTimeField(
        null=True, blank=True,
        help_text="Data e hora que a produção foi finalizada"
    )
    solicitante = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ops_solicitadas'
    )
    
    projeto = models.ForeignKey(
        Projeto, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='ordens_producao',
        help_text="Projeto ao qual esta OP está vinculada"
    )
    demanda_origem = models.ForeignKey(
        Demanda,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_geradas',
        help_text="Demanda de cliente/projeto que originou esta OP."
    )
    quantidade_produzida = models.PositiveIntegerField(
        default=0,
        help_text="Quantidade real que foi produzida com sucesso"
    )
    observacoes = models.TextField(blank=True, null=True)
    custo_estimado = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Custo calculado no momento do planejamento (Qtd * Custo do BOM)"
    )
    custo_real = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Custo real apurado após o consumo de materiais."
    )
    class Meta:
        ordering = ['-data_emissao'] 
        verbose_name = "Ordem de Produção"
        verbose_name_plural = "Ordens de Produção"

    def __str__(self):
        return f"{self.codigo_op or '[NOVA]'} ({self.get_status_display()}) - {self.produto}"

    def save(self, *args, **kwargs):
        if self.pk is None and self.produto:
            if self.produto.custo_producao_calculado is not None:
                qtd = Decimal(self.quantidade_planejada)
                self.custo_estimado = qtd * self.produto.custo_producao_calculado
        
        if not self.id and not self.codigo_op:
            super().save(*args, **kwargs) 
            
            self.codigo_op = f'OP-{self.id:05d}'
            kwargs['force_insert'] = False 
            super().save(update_fields=['codigo_op'], *args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def liberar_producao(self):
        """Muda o status para LIBERADA e dispara a baixa de estoque (BOM)."""
        if self.status == self.StatusOP.PLANEJADA:
            self.status = self.StatusOP.LIBERADA
            self.save(update_fields=['status'])
            # ... (sua lógica futura de baixa de estoque) ...
            print(f"OP {self.codigo_op} liberada. Disparar baixa de estoque.")

    def iniciar_producao(self):
        """Marca a data de início real."""
        if self.status == self.StatusOP.LIBERADA:
            self.status = self.StatusOP.EM_PRODUCAO
            self.data_inicio_real = timezone.now()
            self.save(update_fields=['status', 'data_inicio_real'])
            print(f"OP {self.codigo_op} iniciada.")

    def concluir_producao(self, quantidade_boa):
        """Finaliza a OP e dispara a entrada do produto acabado no estoque."""
        if self.status == self.StatusOP.EM_PRODUCAO or self.status == self.StatusOP.CONTROLE_QUALIDADE:
            self.status = self.StatusOP.CONCLUIDA
            self.data_conclusao_real = timezone.now()
            self.quantidade_produzida = quantidade_boa
            self.save(update_fields=['status', 'data_conclusao_real', 'quantidade_produzida'])
            # ... (sua lógica futura de entrada de estoque) ...
            print(f"OP {self.codigo_op} concluída. Entrada de {quantidade_boa} no estoque.")

# FIM - NÃO ESQUEÇA DE IMPORTAR 'decimal' NO TOPO DO ARQUIVO
# from decimal import Decimal

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

# Em models.py

@receiver(post_save, sender=EstruturaProduto)
def atualizar_preco_produto(sender, instance, **kwargs):
    """
    Calcula o custo total de um ProdutoFabricado somando o custo
    de seus componentes (sejam Matérias-Primas ou outros ProdutosFabricados).
    """
    
    produto = instance.produto_pai 

    estrutura = EstruturaProduto.objects.filter(
        produto_pai=produto
    ).select_related(
        'componente_filho__materiaprima', 
        'componente_filho__produtofabricado'
    )

    total_cost = 0

    for c in estrutura:
        componente = c.componente_filho  # Este é um objeto 'Item' genérico
        custo_componente = 0
        
        if hasattr(componente, 'materiaprima'):
            custo_componente = componente.materiaprima.preco_custo_compra
        elif hasattr(componente, 'produtofabricado'):
            custo_componente = componente.produtofabricado.custo_producao_calculado

        total_cost += (custo_componente * c.quantidade)

    produto.custo_producao_calculado = total_cost
    produto.save(update_fields=['custo_producao_calculado'])

class ItemInstalacao(models.Model):
    """
    Define os 'acessórios' ou 'kits' necessários para a 
    instalação de um produto no cliente (ex: cabos, suportes).
    NÃO é o BOM de fabricação.
    """
    produto_pai = models.ForeignKey(
        ProdutoFabricado, 
        on_delete=models.CASCADE, 
        related_name='itens_instalacao',
        help_text="O produto principal que será instalado."
    )
    item_acessorio = models.ForeignKey(
        Item, 
        on_delete=models.PROTECT, 
        help_text="O item necessário para a instalação (cabo, suporte, etc.)"
    )
    quantidade = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1,
        help_text="Quantidade do acessório necessária por instalação."
    )

    class Meta:
        verbose_name = "Item de Instalação"
        verbose_name_plural = "Itens de Instalação (Kit)"
        # Garante que você não adicione o mesmo cabo duas vezes
        unique_together = ('produto_pai', 'item_acessorio')

    def __str__(self):
        return f"{self.quantidade} x {self.item_acessorio.descricao} (para {self.produto_pai.codigo_item})"

class Volume(models.Model):
    """
    Representa o contêiner físico (a caixa, o pallet).
    Este é o 'Pai' que ganha a etiqueta de rastreio.
    """
    projeto = models.ForeignKey(
        Projeto, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name="volumes"
    )
    codigo_volume = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        help_text="Código único de rastreio deste volume (ex: VOL-0001)"
    )
    data_embalado = models.DateTimeField(
        "Data",
        default=timezone.now
    )
    # Você pode adicionar mais campos ao "Pai" se precisar
    # ex: peso_total, dimensoes, transportadora, etc.

    class Meta:
        verbose_name = "Volume"
        verbose_name_plural = "Volumes"
        ordering = ['-data_embalado']

    def __str__(self):
        return self.codigo_volume

    def save(self, *args, **kwargs):
        # Gera um código de volume automático
        if not self.id and not self.codigo_volume:
            super().save(*args, **kwargs) # Salva para obter um ID
            self.codigo_volume = f'COD-{self.id:05d}'
            kwargs['force_insert'] = False 
            super().save(update_fields=['codigo_volume'], *args, **kwargs)
        else:
            super().save(*args, **kwargs)
# --- MODELO FILHO: O CONTEÚDO DA CAIXA ---
class ItemVolume(models.Model):
    """
    Representa um item DENTRO de um Volume.
    Este é o 'Filho'.
    (Esta é a versão correta do início do seu código)
    """
    volume = models.ForeignKey(
        Volume, 
        on_delete=models.CASCADE, 
        related_name="itens_dentro"
    )
    produto = models.ForeignKey(
        Item, 
        on_delete=models.PROTECT,
        help_text="O produto/material dentro da caixa."
    )
    quantidade = models.DecimalField( # ❗️ O nome correto é 'quantidade'
        "Quantidade",
        max_digits=10, 
        decimal_places=2,
        help_text="Quantidade deste produto neste volume."
    )

    class Meta:
        verbose_name = "Item no Volume"
        verbose_name_plural = "Itens no Volume"
        # Garante que você não adicione o mesmo produto duas vezes na mesma caixa
        unique_together = ('volume', 'produto') 

    def __str__(self):
        # Verifica se 'produto' existe antes de aceder a 'codigo_item'
        if self.produto:
            return f"{self.quantidade} x {self.produto.codigo_item}"
        return f"{self.quantidade} x [PRODUTO INDEFINIDO]"