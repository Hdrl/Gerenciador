from .models import Equipamento, Atividade
# Importe seu model de Produto
from Atividades.models import ProdutoFabricado 

def processar_lista_seriais(atividade, serials_list, form):
    """
    Processa uma lista de seriais vinda do JSON do frontend.
    Valida, cria ou busca equipamentos e adiciona erros ao formulário
    se necessário.
    
    Retorna a lista de objetos Equipamento válidos.
    """
    equipamentos_para_vincular = []
    
    for item in serials_list:
        serial_num = item['serial']
        
        # --- LÓGICA DE MONTAGEM (Tipo 'M') ---
        if atividade.tipoAtividade == 'M':
            # Verifica se o equipamento já existe
            existing_equip = Equipamento.objects.filter(numero_serie=serial_num).first()
            
            if existing_equip:
                # Serial existe. É parte DESTA atividade? (Caso de Edição)
                # 'atividade.equipamentos.all()' funciona mesmo se a atividade for nova (retorna [])
                if existing_equip in atividade.equipamentos.all():
                    equipamentos_para_vincular.append(existing_equip)
                else:
                    # É de outra atividade. ISSO É UM ERRO.
                    form.add_error(None, f"Serial {serial_num} JÁ EXISTE no sistema e não pode ser montado novamente.")
            else:
                # Serial é novo. Crie-o.
                try:
                    produto_obj = ProdutoFabricado.objects.get(id=item['produtoId'])
                    equip = Equipamento.objects.create(
                        numero_serie=serial_num,
                        produto=produto_obj,
                        projeto_alocado=atividade.projeto
                    )
                    equipamentos_para_vincular.append(equip)
                except ProdutoFabricado.DoesNotExist:
                    form.add_error(None, f"Produto (ID: {item['produtoId']}) não encontrado.")

        # --- LÓGICA DE EMBALAGEM (Tipo 'E') ---
        elif atividade.tipoAtividade == 'E':
            try:
                equip = Equipamento.objects.get(numero_serie=serial_num)
                # (Aqui você poderia adicionar a lógica de "já foi montado?")
                equipamentos_para_vincular.append(equip)
            except Equipamento.DoesNotExist:
                form.add_error(None, f"Serial {serial_num} não foi encontrado para embalagem.")
        
        # (Adicione 'elif' para Manutenção 'MA' se necessário)

    return equipamentos_para_vincular