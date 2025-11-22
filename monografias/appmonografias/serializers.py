from rest_framework import serializers
from .models import Aluno, Professor, Monografia, Banca, HistoricoMonografia, HistoricoBanca

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
        
class MonografiaCRUDSerializer(serializers.ModelSerializer):
    """Serializer completo para CRUD (cria, edita, deleta)"""
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Aluno.objects.all(),
        write_only=True,
        label='ID do Aluno'
    )
    orientador_id = serializers.PrimaryKeyRelatedField(
        queryset=Professor.objects.all(),
        write_only=True,
        label='ID do Orientador'
    )
    coorientador_id = serializers.PrimaryKeyRelatedField(
        queryset=Professor.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
        label='ID do Coorientador'
    )
    
    # campos de leitura (dados formatados)
    autor = AlunoSerializer(read_only=True)
    orientador = ProfessorSerializer(read_only=True)
    coorientador = ProfessorSerializer(read_only=True)
    
    class Meta:
        model = Monografia
        fields = ['id', 'titulo', 'autor', 'autor_id', 'orientador', 'orientador_id',
                  'coorientador', 'coorientador_id', 'resumo', 'abstract', 
                  'palavras_chave', 'arquivo', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
    
    def create(self, validated_data):
        """Cria uma nova monografia"""
        autor_id = validated_data.pop('autor_id')
        orientador_id = validated_data.pop('orientador_id')
        coorientador_id = validated_data.pop('coorientador_id', None)
        
        monografia = Monografia.objects.create(
            autor=autor_id,
            orientador=orientador_id,
            coorientador=coorientador_id,
            **validated_data
        )
        return monografia
    
    def update(self, instance, validated_data):
        """Atualiza uma monografia existente"""
        if 'autor_id' in validated_data:
            instance.autor = validated_data.pop('autor_id')
        if 'orientador_id' in validated_data:
            instance.orientador = validated_data.pop('orientador_id')
        if 'coorientador_id' in validated_data:
            instance.coorientador = validated_data.pop('coorientador_id')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class BancaCRUDSerializer(serializers.ModelSerializer):
    """Serializer completo para Banca"""
    monografia_id = serializers.PrimaryKeyRelatedField(
        queryset=Monografia.objects.all(),
        write_only=True,
        label='ID da Monografia'
    )
    professores_avaliadores_ids = serializers.PrimaryKeyRelatedField(
        queryset=Professor.objects.all(),
        many=True,
        write_only=True,
        label='IDs dos Professores Avaliadores'
    )
    
    # campos de leitura
    monografia = MonografiaSerializer(read_only=True)
    professores_avaliadores = ProfessorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Banca
        fields = ['id', 'monografia', 'monografia_id', 'professores_avaliadores',
                  'professores_avaliadores_ids', 'data', 'horario', 'local',
                  'nota_final', 'status']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Cria uma nova banca"""
        monografia = validated_data.pop('monografia_id')
        professores = validated_data.pop('professores_avaliadores_ids')
        
        banca = Banca.objects.create(monografia=monografia, **validated_data)
        banca.professores_avaliadores.set(professores)
        return banca
    
    def update(self, instance, validated_data):
        """Atualiza uma banca"""
        if 'monografia_id' in validated_data:
            instance.monografia = validated_data.pop('monografia_id')
        if 'professores_avaliadores_ids' in validated_data:
            professores = validated_data.pop('professores_avaliadores_ids')
            instance.professores_avaliadores.set(professores)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class HistoricoMonografiaSerializer(serializers.ModelSerializer):
    """Serializer para histórico de monografias"""
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = HistoricoMonografia
        fields = ['id', 'monografia', 'usuario_nome', 'tipo_alteracao', 
                  'campo_alterado', 'valor_anterior', 'valor_novo', 
                  'descricao', 'data_alteracao']
        read_only_fields = ['id', 'data_alteracao']

class HistoricoBancaSerializer(serializers.ModelSerializer):
    """Serializer para histórico de bancas"""
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = HistoricoBanca
        fields = ['id', 'banca', 'usuario_nome', 'tipo_alteracao',
                  'campo_alterado', 'valor_anterior', 'valor_novo',
                  'descricao', 'data_alteracao']
        read_only_fields = ['id', 'data_alteracao']
    """Serializer completo para Banca"""
    monografia_id = serializers.PrimaryKeyRelatedField(
        queryset=Monografia.objects.all(),
        write_only=True,
        label='ID da Monografia'
    )
    professores_avaliadores_ids = serializers.PrimaryKeyRelatedField(
        queryset=Professor.objects.all(),
        many=True,
        write_only=True,
        label='IDs dos Professores Avaliadores'
    )
    
    # campos de leitura
    monografia = MonografiaSerializer(read_only=True)
    professores_avaliadores = ProfessorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Banca
        fields = ['id', 'monografia', 'monografia_id', 'professores_avaliadores',
                  'professores_avaliadores_ids', 'data', 'horario', 'local',
                  'nota_final', 'status']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        """Cria uma nova banca"""
        monografia = validated_data.pop('monografia_id')
        professores = validated_data.pop('professores_avaliadores_ids')
        
        banca = Banca.objects.create(monografia=monografia, **validated_data)
        banca.professores_avaliadores.set(professores)
        return banca
    
    def update(self, instance, validated_data):
        """Atualiza uma banca existente"""
        if 'monografia_id' in validated_data:
            instance.monografia = validated_data.pop('monografia_id')
        if 'professores_avaliadores_ids' in validated_data:
            professores = validated_data.pop('professores_avaliadores_ids')
            instance.professores_avaliadores.set(professores)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance