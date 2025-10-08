import time
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

class RelatorioOrdemServicoDetalhado():
    def register_fonts(self):
        """Registra fontes, se disponíveis."""
        try:
            registerFont(TTFont('Montserrat-Regular', 'Montserrat-Regular.ttf'))
            registerFont(TTFont('Montserrat-Bold', 'Montserrat-Bold.ttf'))
            return "Montserrat-Regular", "Montserrat-Bold"
        except:
            print("Fonte Montserrat não encontrada, usando Helvetica.")
            return "Helvetica", "Helvetica-Bold"

    def draw_header_final(self, c, width, height, dados, font_regular, font_bold):
        """Desenha o cabeçalho final, incluindo o título 'Ordem de Serviço'."""
        # ... (código do logo e info da empresa) ...
        c.setFont(font_bold, 28)
        c.drawString(1.5 * cm, height - 2.5 * cm, "SMART")
        c.setFont(font_bold, 20)
        c.drawString(1.5 * cm, height - 3.2 * cm, "PICKING")
        margin_right = width - 1.5 * cm
        c.setFont(font_bold, 10)
        c.drawRightString(margin_right, height - 2.5 * cm, dados['empresa_nome'])
        c.setFont(font_regular, 9)
        c.drawRightString(margin_right, height - 3.0 * cm, f"CNPJ: {dados['cnpj']}")
        c.drawRightString(margin_right, height - 3.5 * cm, dados['endereco'])
        c.drawRightString(margin_right, height - 4.0 * cm, f"Bairro: {dados['bairro']} - CEP: {dados['cep']} - Telefone: {dados['telefone']}")

        # --- PONTO CHAVE 1: O TÍTULO É DESENHADO AQUI ---
        c.setFont(font_bold, 18)
        c.setFillColor(colors.darkslategray)
        c.drawCentredString(width / 2.0, height - 5.5 * cm, "Ordem de Serviço")

    def draw_body_table(self, c, width, height, dados, font_regular, font_bold):
        """Desenha a tabela principal com os dados da OS."""
        # ... (código de setup de estilos e parágrafos) ...
        styles = getSampleStyleSheet()
        style_normal = styles['BodyText']
        style_normal.fontName = font_regular
        style_normal.fontSize = 10
        style_normal.wordWrap = 'CJK'
        style_normal.leading = 14
        p_analise = Paragraph(dados['analise'], style_normal)
        p_servico = Paragraph(dados['servico_executado'], style_normal)
        header_bg_color = colors.HexColor("#E7E6E6")
        sub_header_bg_color = colors.HexColor("#F2F2F2")
        table_data = [
            ['Código', 'Solicitante', 'Projeto'],
            [dados['os_codigo'], dados['solicitante'], dados['projeto']],
            ['Transportadora', 'Técnico Responsável', 'Local Execução'],
            [dados['transportadora'], dados['tecnico'], dados['local_execucao']],
            ['Equipamento', 'N/S do Equipamento', 'Código de Rastreio'],
            [dados['equipamento'], dados['ns_equipamento'], dados['rastreio']],
            ['Nota Fiscal Entrada', 'Data Início', 'Data Conclusão'],
            [dados['nf_entrada'], dados['data_inicio'], dados['data_conclusao']],
            ['Análise'], [p_analise],
            ['Serviço Executado'], [p_servico]
        ]
        table = Table(table_data, colWidths=[6 * cm, 6 * cm, 6 * cm], rowHeights=None)
        style = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
            ('BACKGROUND', (0, 2), (-1, 2), header_bg_color),
            ('BACKGROUND', (0, 4), (-1, 4), header_bg_color),
            ('BACKGROUND', (0, 6), (-1, 6), header_bg_color),
            ('FONTNAME', (0, 0), (-1, 6), font_bold), ('FONTSIZE', (0, 0), (-1, 6), 10),
            ('FONTNAME', (0, 1), (-1, 7), font_regular), ('FONTSIZE', (0, 1), (-1, 7), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 7), 12), ('TOPPADDING', (0, 0), (-1, 7), 12),
            ('SPAN', (0, 8), (-1, 8)), ('SPAN', (0, 9), (-1, 9)),
            ('SPAN', (0, 10), (-1, 10)), ('SPAN', (0, 11), (-1, 11)),
            ('BACKGROUND', (0, 8), (-1, 8), sub_header_bg_color),
            ('BACKGROUND', (0, 10), (-1, 10), sub_header_bg_color),
            ('FONTNAME', (0, 8), (-1, 10), font_bold), ('ALIGN', (0, 8), (-1, 10), 'LEFT'),
            ('LEFTPADDING', (0, 8), (-1, 10), 8), ('TOPPADDING', (0, 8), (-1, 10), 8),
            ('BOTTOMPADDING', (0, 8), (-1, 10), 8),
            ('ALIGN', (0, 9), (-1, 11), 'LEFT'), ('VALIGN', (0, 9), (-1, 11), 'TOP'),
            ('LEFTPADDING', (0, 9), (-1, 11), 8), ('RIGHTPADDING', (0, 9), (-1, 11), 8),
            ('TOPPADDING', (0, 9), (-1, 11), 8), ('BOTTOMPADDING', (0, 9), (-1, 11), 12),
            ('BOX', (0,0), (-1,-1), 1, colors.darkgrey),
        ])
        table.setStyle(style)

        table.wrapOn(c, width, height)
        # --- PONTO CHAVE 2: A TABELA É DESENHADA AQUI, BEM ABAIXO DO TÍTULO ---
        table.drawOn(c, 1.5 * cm, height - 22 * cm)

    def draw_footer(self, c, width, dados):
        """Desenha o rodapé do documento."""
        # ... (código do rodapé) ...
        footer_color = colors.HexColor("#000000")
        c.setStrokeColor(footer_color)
        c.setLineWidth(2)
        c.line(1.5 * cm, 2.5 * cm, width - 1.5 * cm, 2.5 * cm)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.darkgrey)
        c.drawCentredString(width / 2.0, 1.8 * cm, f"{dados['empresa_nome']} - {dados['telefone']}")

    def gerar_ordem_de_servico_final(self):
        """Função principal para gerar o PDF."""
        file_name = "ordem_servico_269_final.pdf"
        c = canvas.Canvas(file_name, pagesize=A4)
        width, height = A4
        font_regular, font_bold = self.register_fonts()

        dados = {
            "empresa_nome": "SMART PICKING SOLUÇÕES DIGITAIS LTDA",
            "cnpj": "33.055.739/0001-50",
            "telefone": "(43) 3033-4467",
            "endereco": "Rua Desembargador Clotário Portugal, 476 - SALA 02",
            "bairro": "Centro",
            "cep": "86800-020",
            "os_codigo": "269", "solicitante": "LEONARDO", "projeto": "DIME - RJ",
            "transportadora": "CORREIOS", "tecnico": "FERNANDO PEREIRA", "local_execucao": "Empresa",
            "rastreio": "ΟΥ555255896BR", "equipamento": "CONCENTRADOR 12V", "ns_equipamento": "012897",
            "nf_entrada": "1720166", "data_inicio": "16/09/2025", "data_conclusao": "17/09/2025",
            "analise": "SDA Travado em 3V, Defeito Interno no Atmega328p.",
            "servico_executado": (
                "Fios sda e scl soldados nas ilhas A4 e A5, substituído fio dos 5v pull-up para 0,5mm. "
                "Substituída ligação Fonte -> derivador -> arduino, para Fonte -> arduino, soldando nos pinos VIN e GND. "
                "Substituído atmega com defeito interno."
            )
        }

        self.draw_header_final(c, width, height, dados, font_regular, font_bold)
        self.draw_body_table(c, width, height, dados, font_regular, font_bold)
        self.draw_footer(c, width, dados)

        c.save()
        print(f"PDF '{file_name}' gerado com sucesso.")

class RelatorioOrdemServicoGeral:
    def register_fonts(self):
        """Registra fontes."""
        try:
            registerFont(TTFont('Montserrat-Regular', 'Montserrat-Regular.ttf'))
            registerFont(TTFont('Montserrat-Bold', 'Montserrat-Bold.ttf'))
            return "Montserrat-Regular", "Montserrat-Bold"
        except:
            print("Fonte Montserrat não encontrada, usando Helvetica.")
            return "Helvetica", "Helvetica-Bold"

    def draw_header(sefl, c, width, height, dados_os, font_regular, font_bold):
        """Desenha o cabeçalho genérico da OS."""
        c.setFont(font_bold, 28)
        c.drawString(1.5 * cm, height - 2.5 * cm, "SMART")
        c.setFont(font_bold, 20)
        c.drawString(1.5 * cm, height - 3.2 * cm, "PICKING")

        c.setFont(font_bold, 18)
        c.setFillColor(colors.darkslategray)
        c.drawCentredString(width / 2.0, height - 3.5 * cm, f"Ordem de Serviço Simplificada #{dados_os.get('os_codigo', 'N/A')}")
        
        # Informações do solicitante e técnico
        c.setFont(font_bold, 11)
        c.drawString(1.5 * cm, height - 5.5 * cm, "Solicitante:")
        c.drawString(1.5 * cm, height - 6.2 * cm, "Técnico Responsável:")
        
        c.setFont(font_regular, 11)
        c.drawString(5.5 * cm, height - 5.5 * cm, dados_os.get('solicitante', ''))
        c.drawString(5.5 * cm, height - 6.2 * cm, dados_os.get('tecnico', ''))
        
        c.line(1.5 * cm, height - 7 * cm, width - 1.5 * cm, height - 7 * cm)

    def draw_equipamentos_table(self, c, width, height, dados_os, font_regular, font_bold):
        """Desenha a tabela com múltiplos equipamentos."""
        styles = getSampleStyleSheet()
        style_normal = styles['BodyText']
        style_normal.fontName = font_regular
        style_normal.fontSize = 9
        style_normal.wordWrap = 'CJK'
        style_normal.leading = 12

        # Cabeçalho da tabela
        table_data = [
            ['Item', 'Descrição do Equipamento', 'N/S', 'Análise / Serviço Executado']
        ]

        # Adiciona uma linha para cada equipamento na lista
        for i, equip in enumerate(dados_os.get('equipamentos', [])):
            # Cria um Parágrafo para permitir quebra de linha automática no serviço
            servico_paragraph = Paragraph(equip.get('analise_servico', ''), style_normal)
            
            nova_linha = [
                str(i + 1),
                equip.get('descricao', ''),
                equip.get('ns', 'S/N'),
                servico_paragraph
            ]
            table_data.append(nova_linha)

        # Define a largura das colunas
        table = Table(table_data, colWidths=[1.5 * cm, 4.5 * cm, 3 * cm, 9 * cm])
        
        header_bg_color = colors.HexColor("#E7E6E6")
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_bg_color),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Estilo das linhas de dados
            ('FONTNAME', (0, 1), (-1, -1), font_regular),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (2, -1), 'CENTER'), # Centraliza as 3 primeiras colunas
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),   # Alinha a coluna de serviço à esquerda
            ('VALIGN', (0, 1), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Linhas horizontais para um visual limpo
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
        ])
        table.setStyle(style)

        table.wrapOn(c, width, height)
        table.drawOn(c, 1.5 * cm, height - 18 * cm) # Posição inicial da tabela

    def gerar_ordem_de_servico(self, dados_os):
        """
        Função parametrizada que gera um PDF de OS com base nos dados fornecidos.
        """
        file_name = f"os_{dados_os.get('os_codigo', 'sem_numero')}_geral.pdf"
        c = canvas.Canvas(file_name, pagesize=A4)
        width, height = A4
        font_regular, font_bold = self.register_fonts()
        
        self.draw_header(c, width, height, dados_os, font_regular, font_bold)
        self. draw_equipamentos_table(c, width, height, dados_os, font_regular, font_bold)
        # O rodapé foi removido para um visual mais simplificado, mas pode ser adicionado de volta.

        c.save()
        print(f"PDF '{file_name}' gerado com sucesso.")

if __name__ == "__main__":
    dados_para_gerar_os = {
        "os_codigo": "270",
        "solicitante": "DIME - RJ",
        "tecnico": "FERNANDO PEREIRA",
        "data": "05/10/2025",
        
        "equipamentos": [
            {
                "descricao": "CONCENTRADOR 12V",
                "ns": "012897",
                "analise_servico": "Análise: SDA Travado em 3V. Serviço: Substituído microcontrolador Atmega328p."
            },
            {
                "descricao": "PADLOCKPICKING",
                "ns": "013012",
                "analise_servico": "Análise: Tela não liga. Serviço: Realizada a substituição do display LCD 16x2."
            },
            {
                "descricao": "LEITOR BIOMÉTRICO",
                "ns": "S/N",
                "analise_servico": "Análise: Não faz leitura. Serviço: Feita a troca do sensor óptico."
            },
            {
                "descricao": "FONTE DE ALIMENTAÇÃO 12V/2A",
                "ns": "Lote 2024-08",
                "analise_servico": "Análise: Sem tensão na saída. Serviço: Reparo na placa lógica, capacitor C2 trocado."
            }
        ]
    }

    r1 = RelatorioOrdemServicoDetalhado()
    r1.gerar_ordem_de_servico_final()
    r2 = RelatorioOrdemServicoGeral()
    r2.gerar_ordem_de_servico(dados_para_gerar_os)