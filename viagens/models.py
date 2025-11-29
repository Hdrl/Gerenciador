from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

TIPO_CHOICES = [
    ('E', 'Entrada'),
    ('S', 'Saida'),
]

def hoje_meia_noite():
    agora = timezone.now()
    agora_local = timezone.localtime(agora)
    return agora_local.replace(hour=0, minute=0, second=0, microsecond=0)

class Viagem(models.Model):
    destino=models.CharField(max_length=50) 
    empresa=models.CharField(max_length=50, default = "Smart Picking Soluções Digitais Ltda")
    setor=models.CharField(max_length=10, default="Smart")
    colaborador=models.CharField(max_length=50)
    retorno=models.DateField(blank = True, null = True)
    motivo=models.CharField(max_length=50)
    saida=models.CharField(max_length=20, default="Apucarana") 
    usuario=models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.destino} - {self.motivo}"
    
class TransacaoFinanceira(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank = True, null = True, default=0.00)
    descricao = models.CharField(max_length=100, blank = True, null = True, default='-')
    data = models.DateTimeField(blank = True, null = True, default=hoje_meia_noite)
    nota_fiscal = models.URLField(max_length=200, blank = True, null = True, help_text='Url obtida atraves do QRCode')
    imagem = models.ImageField(upload_to='despesas/', blank = True, null = True, help_text='Tirar foto da nota fiscal')

    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name='despesas')
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default='S')
    
    usuario=models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        if not (self.valor and self.descricao and self.data):
            return"—"
        return f"{locale.currency(self.valor, grouping=True)} - {self.descricao.upper()} - {self.data.strftime('%d/%m/%Y %H:%M')}"