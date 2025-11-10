# Nome do arquivo: relatorio_formatado_v5_novadata.py
from collections import Counter
import datetime
import traceback # Importado para capturar o erro completo

CONFIG_CLIENTES = {
    '10.1.6':{
        "NAME":"Medchap PR",
        "IGNORAR_HORA": 10,
        "IGNORAR_MINUTO_MENOR": 2,
        "DEBUG": True
    },
    '192.168.100':{
        "NAME":"Cervosul",
        "IGNORAR_HORA": 6,
        "IGNORAR_MINUTO_MENOR": 2,
        "DEBUG": True
    },
    '172.22.50':{
        "NAME":"DRL",
        "IGNORAR_HORA": -1,
        "IGNORAR_MINUTO_MENOR": -1,
        "DEBUG": True
    },
}


config = {
    "IGNORAR_HORA": 6,
    "IGNORAR_MINUTO_MENOR": 2,
    "DEBUG": True
}

def list_to_planilha(planilha, lista):
    for i, linha in enumerate(lista):
        for j, valor in enumerate(linha):
            planilha.getCellByPosition(j, i).setString(str(valor))

def apply_simple_formatting(planilha):
    """
    Aplica um estilo "zebrado" simples (linhas alternadas) e 
    um cabeçalho em negrito na planilha.
    Também centraliza todo o conteúdo.
    """
    try:
        # 1. Define cores e estilos
        color_header_bg = 0xCCCCCC  # Cinza médio
        color_odd_row_bg = 0xEEEEEE   # Cinza claro
        color_even_row_bg = 0xFFFFFF  # Branco
        font_weight_bold = 150.0 # com.sun.star.awt.FontWeight.BOLD
        HORI_JUSTIFY_CENTER = 2
        
        # 2. Pega a área utilizada da planilha
        cursor = planilha.createCursor()
        cursor.gotoEndOfUsedArea(False)
        last_col = cursor.getRangeAddress().EndColumn
        last_row = cursor.getRangeAddress().EndRow
        
        # 3. Itera e aplica estilo linha por linha
        for r in range(last_row + 1):
            row_range = planilha.getCellRangeByPosition(0, r, last_col, r)
            row_range.setPropertyValue("HoriJustify", HORI_JUSTIFY_CENTER)
            
            if r == 0:
                row_range.setPropertyValue("CellBackColor", color_header_bg)
                row_range.setPropertyValue("CharWeight", font_weight_bold)
            elif r % 2 == 1:
                row_range.setPropertyValue("CellBackColor", color_odd_row_bg)
            else:
                row_range.setPropertyValue("CellBackColor", color_even_row_bg)
    except Exception as e:
        # Se a formatação falhar, isso será logado pelo try/except principal
        raise e


# --- NOVO: Função de Log ---
def log_to_debug_sheet(planilha_debug, row, message):
    """Escreve uma mensagem de log na planilha de debug."""
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        planilha_debug.getCellByPosition(0, row).setString(timestamp)
        planilha_debug.getCellByPosition(1, row).setString(str(message))
        return row + 1
    except Exception:
        # Se nem o log funcionar, não há o que fazer
        return row + 1


def limpar_dados(*args):
    # --- NOVO: Configuração da planilha de debug ---
    doc = XSCRIPTCONTEXT.getDocument()
    planilhas = doc.Sheets
    nome_debug = "Debug_Erros"
    
    if not planilhas.hasByName(nome_debug):
        planilhas.insertNewByName(nome_debug, planilhas.getCount())
    
    planilha_debug = planilhas.getByName(nome_debug)
    planilha_debug.getCellByPosition(0, 0).setString("Timestamp")
    planilha_debug.getCellByPosition(1, 0).setString("Mensagem")
    debug_row = 1 # Começa na linha 1
    # --- Fim da configuração ---

    # --- NOVO: Try/Except GERAL para pegar QUALQUER erro ---
    try:
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Iniciando limpar_dados...")
        
        nome_nova = "Dados Processados"
        nome_nova1 = "Dados Agrupados"
        
        # --- CORREÇÃO: Formato de data atualizado ---
        DATA_FORMAT_2 = "%d/%m/%Y %H:%M" # Formato Dia/Mês/Ano
        DATA_FORMAT_1 = "%Y-%m-%d %H:%M"

        if not planilhas.hasByName(nome_nova):
            planilhas.insertNewByName(nome_nova, planilhas.getCount())
        
        if not planilhas.hasByName(nome_nova1):
            planilhas.insertNewByName(nome_nova1, planilhas.getCount())
        
        dados = planilhas[0]
        informacoes = planilhas.getByName(nome_nova)
        agrupamento = planilhas.getByName(nome_nova1)
        
        linha = 1
        informacoes_set = set()
        informacoes_dict = {}
        
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Iniciando loop de leitura da Planilha 1...")
        
        dados_cell_ip = dados.getCellByPosition(2, 1)
        ip = dados_cell_ip.getString()  
        if not ip:
            raise ValueError("A célula C2 (configuração de IP) está vazia.")
        ip_cutted = '.'.join(ip.split('.')[:3])
        config_cliente = CONFIG_CLIENTES.get(ip_cutted) 

        if config_cliente:
            config = config_cliente
            debug_row = log_to_debug_sheet(planilha_debug, debug_row, f"CONFIGURADO PARA {config['NAME']}...")
        else:
            debug_row = log_to_debug_sheet(planilha_debug, debug_row, f"AVISO: IP {ip_cutted} não encontrado em CONFIG_CLIENTES. Usando config padrão.")
            pass

        while True:
            dados_cell_timestamp = dados.getCellByPosition(1, linha)
            dados_cell_ip = dados.getCellByPosition(2, linha)
            dados_cell_firmware = dados.getCellByPosition(3, linha)
            
            data_bruta = dados_cell_timestamp.getString()
            
            if(linha % 50 == 0): # Log a cada 50 linhas para não poluir
                debug_row = log_to_debug_sheet(planilha_debug, debug_row, f"Processando linha {linha+1}...")
            
            if(data_bruta == ""):
                debug_row = log_to_debug_sheet(planilha_debug, debug_row, f"Fim dos dados encontrado na linha {linha+1}. Saindo do loop.")
                break
            
            # Pega os primeiros 16 caracteres.
            # "21/10/2025 06:01:08" -> "21/10/2025 06:01"
            data = data_bruta[:16] 
            ip = dados_cell_ip.getString()
            firmware_version = dados_cell_firmware.getString()
            
            try:
                data_convertida = datetime.datetime.strptime(data, DATA_FORMAT_2)
            except ValueError as e:
                try: 
                    data_convertida = datetime.datetime.strptime(data, DATA_FORMAT_1)
                except ValueError as e:
                    # --- MODIFICADO: Loga o erro na PLANILHA ---
                    erro_msg = f"ERRO ao converter data na linha {linha+1}. String: '{data}'. Data Bruta: '{data_bruta}'. Erro: {e}"
                    print(erro_msg) # Mantém o print
                    debug_row = log_to_debug_sheet(planilha_debug, debug_row, erro_msg) # Adiciona log na planilha
                    linha = linha + 1
                    continue    

            if not(data_convertida.hour == config["IGNORAR_HORA"] and data_convertida.minute <= config["IGNORAR_MINUTO_MENOR"]):
                informacoes_set.add((data_convertida, ip, firmware_version)) 
            
            linha = linha + 1
        
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Loop de leitura finalizado. Itens únicos no set: " + str(len(informacoes_set)))
        
        if config["DEBUG"]:
            debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Modo DEBUG. Criando planilha 'Debug 1'...")
            nome_nova2 = "Debug 1"
            if not planilhas.hasByName(nome_nova2):
                planilhas.insertNewByName(nome_nova2, planilhas.getCount())
            
            debug_list = [(dt.strftime(DATA_FORMAT_2), ip, fw) for dt, ip, fw in informacoes_set]
            list_to_planilha(planilhas.getByName(nome_nova2), debug_list)
            debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Planilha 'Debug 1' preenchida.")

        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Iniciando processamento 'informacoes_dict'...")
        for item in informacoes_set:
            data_convertida, ip, firmware_version = item
            chave_data = data_convertida.date() # Pega a data (ex: 2025-10-21)
            if not(chave_data in informacoes_dict.keys()):
               informacoes_dict[chave_data] = [ip]
            else:
                informacoes_dict[chave_data].append(ip)
        
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Dicionário 'informacoes_dict' criado. Iniciando contagem (Counter)...")
        contagens_por_chave = {}
        for chave, lista_de_ips in informacoes_dict.items():
            contagens_por_chave[chave] = Counter(lista_de_ips)

        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Contagem finalizada. Preenchendo planilha 'Dados Processados'...")
        for col, (chave, distribuicao_ip) in enumerate(sorted(contagens_por_chave.items())):
            data_formatada = chave.strftime("%d/%m/%Y")
            informacoes.getCellByPosition(col*2, 0).setString(f"Dia {data_formatada}")
            informacoes.getCellByPosition(col*2+1, 0).setString(f"Contagem {data_formatada}")
            for linha_saida, (ip, count) in enumerate(distribuicao_ip.items(), start=1):
                informacoes.getCellByPosition(col*2, linha_saida).setString(ip)
                informacoes.getCellByPosition(col*2+1, linha_saida).setString(str(count))
        
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Preenchendo planilha 'Dados Agrupados'...")
        ips = []
        agrupamento.getCellByPosition(0, 0).setString("IPS")
        
        for col, (chave, distribuicao_ip) in enumerate(sorted(contagens_por_chave.items()), start=1):
      
            # --- MUDANÇA AQUI ---
            data_formatada = chave.strftime("%d/%m/%Y")
            agrupamento.getCellByPosition(col, 0).setString(f"Dia {data_formatada}")
            # --- FIM DA MUDANÇA ---
      
            for (ip, count) in distribuicao_ip.items():
                if not ip in ips:
                    agrupamento.getCellByPosition(0, len(ips) + 1).setString(ip)
                    agrupamento.getCellByPosition(col, len(ips) + 1).setValue(count)
                    ips.append(ip)
                else:
                    agrupamento.getCellByPosition(col, ips.index(ip) + 1).setValue(count)
        
        total_dias = len(contagens_por_chave.keys())
        agrupamento.getCellByPosition(total_dias + 1, 0).setString("Total")
        agrupamento.getCellByPosition(total_dias + 2, 0).setString("Media")
        
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Iniciando cálculo de Total e Média...")
        
        for row_index in range(len(ips)):
            current_row = row_index + 1
            row_total = 0.0
            active_days_count = 0
            
            for col_index in range(total_dias):
                current_col = col_index + 1
                cell = agrupamento.getCellByPosition(current_col, current_row)
                cell_value = cell.getValue()
                row_total += cell_value
                if cell_value > 0:
                    active_days_count += 1
            
            if active_days_count > 0:
                row_average = row_total / active_days_count
            else:
                row_average = 0.0
            
            row_average_int = round(row_average) 
                
            total_col = total_dias + 1
            media_col = total_dias + 2
            agrupamento.getCellByPosition(total_col, current_row).setValue(row_total)
            agrupamento.getCellByPosition(media_col, current_row).setValue(row_average_int)

        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "Cálculos finalizados. Iniciando formatação...")
        
        apply_simple_formatting(informacoes)
        apply_simple_formatting(agrupamento)
        
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, "--- SCRIPT FINALIZADO COM SUCESSO ---")

    except Exception as e:
        # --- NOVO: Pega-tudo para erros GERAIS ---
        erro_geral = f"ERRO GERAL INESPERADO: {e}\n{traceback.format_exc()}"
        print(erro_geral)
        debug_row = log_to_debug_sheet(planilha_debug, debug_row, erro_geral)

g_exportedScripts = (limpar_dados,)