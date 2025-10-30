from rest_framework import serializers
from Atividades.models import User, Endereco, Projeto, ProdutoFabricado, OrdemServico, OrdemProducao

class OrdemServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdemServico
        fields = '__all__'

class OrdemProducaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdemProducao
        fields = '__all__'

class ProdutoFabricadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoFabricado
        fields = '__all__'

class ProjetoSerializer(serializers.ModelSerializer):  
    class Meta:
        model = Projeto
        fields = '__all__'

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'