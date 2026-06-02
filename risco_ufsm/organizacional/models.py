"""
organizacional/models.py

Estrutura organizacional.
Soft delete em todos os modelos — nada é apagado fisicamente.
Histórico de vínculos preservado.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Unidade(models.Model):
    TIPO_CHOICES = [
        ('REITORIA',     'Reitoria'),
        ('PRO_REITORIA', 'Pró-Reitoria'),
        ('CENTRO',       'Centro de Ensino'),
        ('ORGAO',        'Órgão Suplementar'),
        ('CAMPUS',       'Campus'),
    ]

    nome       = models.CharField('Nome', max_length=200)
    sigla      = models.CharField('Sigla', max_length=20, blank=True)
    tipo       = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    ativo      = models.BooleanField('Ativo', default=True)
    deleted_at = models.DateTimeField('Excluído em', null=True, blank=True)
    criado_em  = models.DateTimeField('Criado em', auto_now_add=True)
    history    = HistoricalRecords()

    class Meta:
        verbose_name         = 'Unidade'
        verbose_name_plural  = 'Unidades'
        ordering             = ['nome']

    def __str__(self):
        return f'{self.sigla} — {self.nome}' if self.sigla else self.nome

    def soft_delete(self):
        self.ativo = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['ativo', 'deleted_at'])

    def get_setores_ativos(self):
        return self.setores.filter(ativo=True)


class Setor(models.Model):
    unidade    = models.ForeignKey(Unidade, on_delete=models.PROTECT, related_name='setores')
    nome       = models.CharField('Nome', max_length=200)
    sigla      = models.CharField('Sigla', max_length=20, blank=True)
    ativo      = models.BooleanField('Ativo', default=True)
    deleted_at = models.DateTimeField('Excluído em', null=True, blank=True)
    criado_em  = models.DateTimeField('Criado em', auto_now_add=True)
    history    = HistoricalRecords()

    class Meta:
        verbose_name         = 'Setor / Subunidade'
        verbose_name_plural  = 'Setores / Subunidades'
        ordering             = ['unidade__nome', 'nome']

    def __str__(self):
        return f'{self.unidade.sigla} › {self.nome}' if self.unidade.sigla \
            else f'{self.unidade.nome} › {self.nome}'

    def soft_delete(self):
        self.ativo = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['ativo', 'deleted_at'])


class UsuarioSetor(models.Model):
    """
    Vínculo N:N entre Usuário e Setor.

    Regras:
    - Nunca é apagado fisicamente (soft delete via ativo/data_fim)
    - Histórico preservado para auditoria
    - Um usuário pode ter múltiplos setores simultâneos
    - Troca de setor: data_fim no vínculo anterior + novo vínculo
    """
    usuario     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='usuario_setores',
        verbose_name='Usuário',
    )
    setor       = models.ForeignKey(
        Setor,
        on_delete=models.PROTECT,
        related_name='membros',
        verbose_name='Setor',
    )
    data_inicio = models.DateField('Data de Início', default=timezone.localdate)
    data_fim    = models.DateField('Data de Fim', null=True, blank=True)
    ativo       = models.BooleanField('Ativo', default=True, db_index=True)
    criado_por  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='vinculos_criados',
        verbose_name='Criado por',
    )
    criado_em   = models.DateTimeField('Criado em', auto_now_add=True)
    history     = HistoricalRecords()

    class Meta:
        verbose_name         = 'Vínculo Usuário–Setor'
        verbose_name_plural  = 'Vínculos Usuário–Setor'
        ordering             = ['-ativo', '-data_inicio']

    def __str__(self):
        status = 'ativo' if self.ativo else 'encerrado'
        return f'{self.usuario.get_nome_completo()} → {self.setor} [{status}]'

    def encerrar(self, data_fim=None):
        """Encerra o vínculo (nunca apaga)."""
        self.ativo    = False
        self.data_fim = data_fim or timezone.localdate()
        self.save(update_fields=['ativo', 'data_fim'])
