"""
Log de alterações genérico — registra qualquer mudança no sistema.
Imutável: nenhum registro pode ser apagado.
"""
from django.conf import settings
from django.db import models


class LogAlteracao(models.Model):
    """Log de alteração genérico e imutável de qualquer objeto do sistema."""

    model_name      = models.CharField('Model', max_length=100)
    objeto_id       = models.PositiveIntegerField('ID do objeto')
    campo           = models.CharField('Campo alterado', max_length=100, blank=True)
    valor_anterior  = models.TextField('Valor anterior', blank=True)
    valor_novo      = models.TextField('Valor novo', blank=True)
    descricao       = models.TextField('Descrição', blank=True)
    usuario         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs_alteracao',
        verbose_name='Usuário',
    )
    ip              = models.GenericIPAddressField('IP', null=True, blank=True)
    criado_em       = models.DateTimeField('Data/Hora', auto_now_add=True, db_index=True)

    class Meta:
        """Metadados do model: nome legível e ordenação decrescente por data."""

        verbose_name         = 'Log de Alteração'
        verbose_name_plural  = 'Logs de Alteração'
        ordering             = ['-criado_em']

    def __str__(self):
        return (f'[{self.criado_em:%d/%m/%Y %H:%M}] '
                f'{self.model_name}#{self.objeto_id} — {self.campo}')

    def delete(self, *args, **kwargs):
        raise PermissionError('Logs de alteração não podem ser apagados.')
