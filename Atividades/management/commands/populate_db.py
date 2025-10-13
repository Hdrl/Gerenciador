import json
from pathlib import Path # Para lidar com caminhos de arquivos de forma moderna
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings # Para pegar o caminho base do projeto
from Atividades.models import Fornecedor, Item, MateriaPrima, ProdutoFabricado, EstruturaProduto

class Command(BaseCommand):
    help = 'Popula o banco de dados a partir de um arquivo JSON de fixtures.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Limpando dados antigos...'))
        EstruturaProduto.objects.all().delete()
        # A herança multi-tabela exige que os filhos sejam deletados primeiro
        MateriaPrima.objects.all().delete()
        ProdutoFabricado.objects.all().delete()
        Fornecedor.objects.all().delete()
        Item.objects.all().delete()

        # 1. CARREGAR DADOS DO ARQUIVO JSON
        # Constrói o caminho para o arquivo de forma segura
        json_path = Path(settings.BASE_DIR) / 'Atividades' / 'fixtures' / 'dados_iniciais.json'
        self.stdout.write(f"Lendo dados de '{json_path}'...")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 2. CRIAR OBJETOS - A ORDEM É IMPORTANTE!
        
        # Criar Fornecedores
        fornecedores_data = data.get('fornecedores', [])
        for f_data in fornecedores_data:
            Fornecedor.objects.create(**f_data)
        self.stdout.write(self.style.SUCCESS(f"{len(fornecedores_data)} fornecedores criados."))
        
        # Mapear CNPJ para objeto Fornecedor para consulta rápida
        fornecedores_map = {f.cnpj: f for f in Fornecedor.objects.all()}

        # Criar Matérias-Primas
        materias_primas_data = data.get('materias_primas', [])
        for mp_data in materias_primas_data:
            # Pega o CNPJ do JSON e encontra o objeto Fornecedor correspondente
            fornecedor_cnpj = mp_data.pop('fornecedor_padrao_cnpj', None)
            mp_data['fornecedor_padrao'] = fornecedores_map.get(fornecedor_cnpj)
            MateriaPrima.objects.create(**mp_data)
        self.stdout.write(self.style.SUCCESS(f"{len(materias_primas_data)} matérias-primas criadas."))

        # Criar Produtos Fabricados
        produtos_fabricados_data = data.get('produtos_fabricados', [])
        for pf_data in produtos_fabricados_data:
            ProdutoFabricado.objects.create(**pf_data)
        self.stdout.write(self.style.SUCCESS(f"{len(produtos_fabricados_data)} produtos fabricados criados."))

        # Mapear codigo_item para objeto Item para a montagem da estrutura
        items_map = {item.codigo_item: item for item in Item.objects.all()}
        produtos_fabricados_map = {pf.codigo_item: pf for pf in ProdutoFabricado.objects.all()}
        
        # Montar Estrutura de Produto
        estrutura_data = data.get('estrutura_produto', [])
        for est_data in estrutura_data:
            pai_codigo = est_data['produto_pai_codigo']
            filho_codigo = est_data['componente_filho_codigo']
            
            produto_pai_obj = produtos_fabricados_map.get(pai_codigo)
            componente_filho_obj = items_map.get(filho_codigo)

            if produto_pai_obj and componente_filho_obj:
                EstruturaProduto.objects.create(
                    produto_pai=produto_pai_obj,
                    componente_filho=componente_filho_obj,
                    quantidade=est_data['quantidade']
                )
            else:
                self.stdout.write(self.style.ERROR(f"Erro ao montar estrutura: item '{pai_codigo}' ou '{filho_codigo}' não encontrado."))
        self.stdout.write(self.style.SUCCESS(f"{len(estrutura_data)} relações de estrutura criadas."))
        
        # 3. EXECUTAR LÓGICAS (como cálculo de custo)
        self.stdout.write(self.style.WARNING('Calculando custos de produção...'))
        
        def calcular_custo(produto_fabricado):
            # Esta função permanece a mesma da versão anterior
            custo_total = 0
            for componente_estrutura in produto_fabricado.componentes.all():
                componente = componente_estrutura.componente_filho
                quantidade = componente_estrutura.quantidade
                
                if hasattr(componente, 'materiaprima'):
                    custo_total += componente.materiaprima.preco_custo_compra * quantidade
                elif hasattr(componente, 'produtofabricado'):
                    if componente.produtofabricado.custo_producao_calculado == 0:
                        calcular_custo(componente.produtofabricado)
                    custo_total += componente.produtofabricado.custo_producao_calculado * quantidade
            
            produto_fabricado.custo_producao_calculado = custo_total
            produto_fabricado.save()
            self.stdout.write(f"Custo de '{produto_fabricado.descricao}' calculado: R$ {custo_total:.2f}")

        # Inicia o cálculo a partir de todos os produtos fabricados
        for pf in ProdutoFabricado.objects.order_by('pk'): # Ordena para garantir consistência
            if pf.custo_producao_calculado == 0:
                calcular_custo(pf)

        self.stdout.write(self.style.SUCCESS('\nProcesso de povoamento via JSON concluído com sucesso!'))