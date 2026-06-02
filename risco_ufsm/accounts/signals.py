"""
O signals automaticamente registra logs de alterações em usuários e vínculos com setores
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver
from auditoria.models import LogAlteracao

logger = logging.getLogger('accounts')

@receiver(post_save, sender='accounts.Usuario')
def log_alteracao_usuario(_sender, instance, created, **_kwargs):
    '''classe para registrar logs de criação e atualização de usuários.'''
    try:
        descricao = 'Usuário criado' if created else 'Usuário atualizado'
        # pylint: disable=no-member
        # Desabilitei `no-member` porque `LogAlteracao` é um modelo Django e
        # o linter pode não reconhecer seus campos dinamicamente.
        LogAlteracao.objects.create(
            model_name='Usuario',
            objeto_id=instance.pk,
            descricao=descricao,
            campo='geral',
            valor_novo=str(instance),
        )
    except Exception as e:
        logger.error('Erro ao registrar log de alteração de usuário: %s', e)
        raise


@receiver(post_save, sender='organizacional.UsuarioSetor')
def log_vinculo_usuario_setor(_sender, instance, created, **_kwargs):
    '''Classe para registrar logs de criação e atualização de
    vínculos entre usuários e setores.'''
    try:
        descricao = (
            f'Vínculo criado: {instance.usuario} → {instance.setor}'
            if created else
            f'Vínculo atualizado: {instance.usuario} → {instance.setor}'
        )
        # pylint: disable=no-member
        LogAlteracao.objects.create(
            model_name='UsuarioSetor',
            objeto_id=instance.pk,
            descricao=descricao,
            campo='vinculo',
            valor_novo=str(instance),
        )
    except Exception as e:
        logger.error('Erro ao registrar log de vínculo: %s', e)
        raise
