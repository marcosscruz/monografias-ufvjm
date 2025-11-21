from rest_framework import serializers
from .models import Aluno, Professor, Monografia, Banca

class ProfessorSerializer(serializers.ModelSerializer):
    """Serializer para Professor - converte modelo em JSON"""
    nome = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Professor
        fields = ['id', 'nome', 'email', 'titulação', 'area_pesquisa']

class AlunoSerializer(serializers.ModelSerializer):
    """Serializer para Aluno - converte modelo em JSON"""
    nome = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'email', 'matricula']

class MonografiaSerializer(serializers.ModelSerializer):
    """Serializer para Monografia - converte modelo em JSON"""
    autor = AlunoSerializer(read_only=True)
    orientador = ProfessorSerializer(read_only=True)
    coorientador = ProfessorSerializer(read_only=True)
    
    class Meta:
        model = Monografia
        fields = ['id', 'titulo', 'autor', 'orientador', 'coorientador', 
                  'resumo', 'abstract', 'palavras_chave', 'arquivo', 
                  'criado_em', 'atualizado_em']

class BancaSerializer(serializers.ModelSerializer):
    """Serializer para Banca - converte modelo em JSON"""
    monografia = MonografiaSerializer(read_only=True)
    professores_avaliadores = ProfessorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Banca
        fields = ['id', 'monografia', 'professores_avaliadores', 'data', 
                  'horario', 'local', 'nota_final', 'status']