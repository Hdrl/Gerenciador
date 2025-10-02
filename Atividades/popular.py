import json


with open('Atividades\static\Atividades\json\dados.json', 'r', encoding='utf-8') as file:
    dados = json.load(file)

print(dados)