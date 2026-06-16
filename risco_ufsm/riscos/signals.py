from django.db.models.signals import post_save
from django.dispatch import receiver
from auditoria.models import LogAlteracao
from .models import PlanoDeRisco, AvaliacaoRisco, TratamentoRisco

@receiver(post_save, sender=PlanoDeRisco)
def log_plano(sender, instance, created, **kwargs):
    descricao = 'Plano criado' if created else f'Plano atualizado — status: {instance.status}'
    LogAlteracao.objects.create(
        model_name='PlanoDeRisco',
        objeto_id=instance.pk,
        descricao=descricao,
    )

@receiver(post_save, sender=AvaliacaoRisco)
def log_avaliacao(sender, instance, created, **kwargs):
    descricao = (f'Avaliação {"criada" if created else "atualizada"} — '
                 f'RI: {instance.risco_inerente} ({instance.nivel_inerente}), '
                 f'RR: {instance.risco_residual} ({instance.nivel_residual})')
    LogAlteracao.objects.create(
        model_name='AvaliacaoRisco',
        objeto_id=instance.pk,
        descricao=descricao,
    )