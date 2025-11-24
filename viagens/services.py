from bs4 import BeautifulSoup as bs4
from urllib.parse import urlparse
import requests, re, datetime

def extrair_url(url):
    transacao_financeira = {'descricao': '', 'data':None, 'valor':0};
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers)
    if not response:
        return false
    if response.status_code == 200:
        hostname = urlparse(url).hostname
        soup = bs4(response.text, "html.parser")
        if hostname == 'portalsped.fazenda.mg.gov.br':
            #descricao
            desc_transacao = soup.select(r'#formPrincipal\:content-template-consulta > div.container > table.table.text-center > thead > tr:nth-child(2) > th > h4 > b')
            if desc_transacao:
                transacao_financeira['descricao'] = desc_transacao[0].text
            #valor
            valor_transacao = soup.select(r'#formPrincipal\:content-template-consulta > div.container > div:nth-child(8) > div.col-lg-2 > strong')
            if valor_transacao:
                transacao_financeira['valor'] = valor_transacao[0].text.replace(',', '.')
            #data
            r_str = r"\b\d{2}/\d{2}/\d{4}\b \b\d{2}:\d{2}:\d{2}\b"
            dtime = re.search(r_str, response.text)
            if dtime:
                transacao_financeira['data'] = datetime.datetime.strptime(dtime.group(), "%d/%m/%Y %H:%M:%S")
        elif hostname == 'www.fazenda.pr.gov.br':
            #descricao
            desc_transacao = soup.find_all(id="u20")
            if desc_transacao:
                transacao_financeira['descricao'] = desc_transacao[0].text
            #valor
            valor_transacao = soup.find_all(class_="totalNumb txtMax")
            if valor_transacao:
                transacao_financeira['valor'] = valor_transacao[0].text.replace(',', '.')
            #data
            r_str = r"\b\d{2}/\d{2}/\d{4}\b \b\d{2}:\d{2}:\d{2}\b"
            dtime = re.search(r_str, response.text)
            if dtime:
                transacao_financeira['data'] = datetime.datetime.strptime(dtime.group(), "%d/%m/%Y %H:%M:%S")
    return transacao_financeira

def extrair_url_selecionada(modeladmin, request, queryset):
    for receita in queryset:
        transacao = extrair_url(receita.nota_fiscal)
        receita.descricao = transacao['descricao']
        receita.valor = transacao['valor']
        receita.data = transacao['data']
        receita.save()