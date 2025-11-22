from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver
from .models import Monografia, Banca, HistoricoMonografia, HistoricoBanca

# Dicionário para armazenar estado anterior (na memória)
_pre_save_state = {}

@receiver(post_migrate)
def criar_grupos(sender, **kwargs):
    for nome in ['Administrador', 'Professor', 'Aluno']:
        Group.objects.get_or_create(name=nome)
        
@receiver(pre_save, sender=Monografia)
def registrar_estado_anterior_monografia(sender, instance, **kwargs):
    """
    Registra o estado anterior da monografia antes de salvar
    """
    if instance.pk:
        try:
            anterior = Monografia.objects.get(pk=instance.pk)
            _pre_save_state[f'monografia_{instance.pk}'] = {
                'titulo': anterior.titulo,
                'resumo': anterior.resumo,
                'abstract': anterior.abstract,
                'palavras_chave': anterior.palavras_chave,
                'orientador_id': anterior.orientador_id,
                'coorientador_id': anterior.coorientador_id,
                'arquivo': str(anterior.arquivo),
            }
        except Monografia.DoesNotExist:
            pass

@receiver(post_save, sender=Monografia)
def registrar_alteracao_monografia(sender, instance, created, **kwargs):
    """
    Registra criação ou edição de monografia no histórico
    """
    from django.contrib.auth.models import AnonymousUser
    
    # Obtém o usuário da request (se disponível)
    usuario = getattr(instance, '_usuario_atual', None)
    
    if created:
        # Registra criação
        HistoricoMonografia.objects.create(
            monografia=instance,
            usuario=usuario,
            tipo_alteracao='CRIACAO',
            descricao=f'Monografia "{instance.titulo}" foi criada'
        )
    else:
        # Registra edição
        estado_anterior = _pre_save_state.get(f'monografia_{instance.pk}', {})
        
        if estado_anterior:
            campos_alterados = []
            
            # Verifica cada campo
            if estado_anterior.get('titulo') != instance.titulo:
                HistoricoMonografia.objects.create(
                    monografia=instance,
                    usuario=usuario,
                    tipo_alteracao='EDICAO',
                    campo_alterado='titulo',
                    valor_anterior=estado_anterior.get('titulo'),
                    valor_novo=instance.titulo
                )
                campos_alterados.append('título')
            
            if estado_anterior.get('resumo') != instance.resumo:
                campos_alterados.append('resumo')
            
            if estado_anterior.get('abstract') != instance.abstract:
                campos_alterados.append('abstract')
            
            if estado_anterior.get('palavras_chave') != instance.palavras_chave:
                campos_alterados.append('palavras-chave')
            
            if estado_anterior.get('arquivo') != str(instance.arquivo):
                campos_alterados.append('arquivo')
            
            # Se houve alterações, registra um histórico geral
            if campos_alterados:
                HistoricoMonografia.objects.create(
                    monografia=instance,
                    usuario=usuario,
                    tipo_alteracao='EDICAO',
                    descricao=f'Campos alterados: {", ".join(campos_alterados)}'
                )
            
            # Remove do dicionário
            _pre_save_state.pop(f'monografia_{instance.pk}', None)

# ========== BANCA ==========
@receiver(pre_save, sender=Banca)
def registrar_estado_anterior_banca(sender, instance, **kwargs):
    """Registra estado anterior da banca"""
    if instance.pk:
        try:
            anterior = Banca.objects.get(pk=instance.pk)
            _pre_save_state[f'banca_{instance.pk}'] = {
                'data': anterior.data,
                'horario': anterior.horario,
                'local': anterior.local,
                'nota_final': anterior.nota_final,
                'status': anterior.status,
            }
        except Banca.DoesNotExist:
            pass

@receiver(post_save, sender=Banca)
def registrar_alteracao_banca(sender, instance, created, **kwargs):
    """Registra alterações na banca"""
    usuario = getattr(instance, '_usuario_atual', None)
    
    if created:
        HistoricoBanca.objects.create(
            banca=instance,
            usuario=usuario,
            tipo_alteracao='CRIACAO',
            descricao=f'Banca para "{instance.monografia.titulo}" foi criada'
        )
    else:
        estado_anterior = _pre_save_state.get(f'banca_{instance.pk}', {})
        
        if estado_anterior:
            campos_alterados = []
            
            if estado_anterior.get('nota_final') != instance.nota_final:
                HistoricoBanca.objects.create(
                    banca=instance,
                    usuario=usuario,
                    tipo_alteracao='EDICAO',
                    campo_alterado='nota_final',
                    valor_anterior=str(estado_anterior.get('nota_final')),
                    valor_novo=str(instance.nota_final)
                )
                campos_alterados.append('nota final')
            
            if estado_anterior.get('status') != instance.status:
                HistoricoBanca.objects.create(
                    banca=instance,
                    usuario=usuario,
                    tipo_alteracao='EDICAO',
                    campo_alterado='status',
                    valor_anterior=estado_anterior.get('status'),
                    valor_novo=instance.status
                )
                campos_alterados.append('status')
            
            if estado_anterior.get('data') != instance.data:
                campos_alterados.append('data')
            
            if estado_anterior.get('local') != instance.local:
                campos_alterados.append('local')
            
            if campos_alterados:
                HistoricoBanca.objects.create(
                    banca=instance,
                    usuario=usuario,
                    tipo_alteracao='EDICAO',
                    descricao=f'Campos alterados: {", ".join(campos_alterados)}'
                )
            
            _pre_save_state.pop(f'banca_{instance.pk}', None)
