"""
O signals automaticamente registra logs de alterações em usuários e vínculos com setores

"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger('accounts')


@receiver(post_save, sender='accounts.Usuario')
def log_alteracao_usuario(sender, instance, created, **kwargs):
    try:
        from auditoria.models import LogAlteracao
        descricao = 'Usuário criado' if created else 'Usuário atualizado'
        LogAlteracao.objects.create(
            model_name='Usuario',
            objeto_id=instance.pk,
            descricao=descricao,
            campo='geral',
            valor_novo=str(instance),
        )
    except Exception as exc:
        logger.error('Erro ao registrar log de alteração de usuário: %s', exc)


@receiver(post_save, sender='organizacional.UsuarioSetor')
def log_vinculo_usuario_setor(sender, instance, created, **kwargs):
    try:
        from auditoria.models import LogAlteracao
        descricao = (
            f'Vínculo criado: {instance.usuario} → {instance.setor}'
            if created else
            f'Vínculo atualizado: {instance.usuario} → {instance.setor}'
        )
        LogAlteracao.objects.create(
            model_name='UsuarioSetor',
            objeto_id=instance.pk,
            descricao=descricao,
            campo='vinculo',
            valor_novo=str(instance),
        )
    except Exception as exc:
        logger.error('Erro ao registrar log de vínculo: %s', exc)
