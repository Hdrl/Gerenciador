from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Atividade(models.Model):
    idAtividade = models.AutoField(primary_key=True)
    dataInicial = models.DateTimeField()
    dataFinal = models.DateTimeField()
    situacao = models.CharField(max_length=50)

class Peca

class Equipamento():
    id = models.AutoField(primary_key=True)
    serialNumber = models.CharField(max_length=50)
    descricao = models.CharField(max_length=100)


class Problema(models.Model):
    idProblema = models.AutoField(primary_key=True)
    descricao = models.CharField(max_length=100)

class OrdemServico(models.Model):
    idOrdemServico = models.AutoField(primary_key=True)
    solicitante = models.CharField(max_length=100)
    localExecucao = models.CharField(max_length=100)
    Projeto = models.CharField(max_length=100)
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