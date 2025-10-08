from source.jsonHandler import jsonHandler
import time
from django.core.management.base import BaseCommand
from Atividades.models import *

class Command(BaseCommand):
    args = ""
    help = "comando que popula as tabelas do banco de dados"

    def _create_equipamentos(self):
        start_time = time.time()
        self.stdout.write("Limpando tabela equipamentos...")
        Equipamento.objects.all().delete()
        self.stdout.write("salvando equipamentos...")
        equipamentos = jsonHandler('./source/json/equipamentos.json').read_json()
        for equipamento in equipamentos:
            aux = TipoEquipamento()
            aux.idEquipamento = equipamento['idEquipamento']
            aux.descricao = equipamento['descricao']
            aux.save()
        self.stdout.write(f"---- {(time.time() - start_time):.2f} Segundos ----")
    
    def _create_problemas(self):
        start_time = time.time()
        self.stdout.write("Limpando tabela problemas...")
        Problema.objects.all().delete()
        self.stdout.write("salvando problema...")
        problemas = jsonHandler('./source/json/problema.json').read_json()
        for problema in problemas:
            aux = Problema()
            aux.idProblema = problema['idTipoProblema']
            aux.descricao = problema['descricao']
            aux.save()
        self.stdout.write(f"---- {(time.time() - start_time):.2f} Segundos ----")

    def handle(self, *args, **options):
        self._create_equipamentos()
        self._create_problemas()