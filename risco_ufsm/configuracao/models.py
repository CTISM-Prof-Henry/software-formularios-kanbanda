"""Módulo de modelos para a estrutura de configuração do PDI e Macroprocessos."""
from django.db import models
from django.utils import timezone


class DesafioPDI(models.Model):
    """Modelo que representa os Desafios do Plano de Desenvolvimento Institucional (PDI)."""
    numero = models.IntegerField()
    descricao = models.CharField(max_length=300)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Metadados de configuração para o modelo DesafioPDI."""
        verbose_name = 'Desafio PDI'
        verbose_name_plural = 'Desafios PDI'
        ordering = ['numero']

    def __str__(self):
        """Retorna a representação textual do objeto em formato string."""
        return f"Desafio {self.numero} - {str(self.descricao)[:50]}"

    def soft_delete(self):
        """Realiza a exclusão lógica do registro definindo a data de deleção."""
        self.deleted_at = timezone.now()
        self.ativo = False # Marca como inativo
        self.save(update_fields=['deleted_at', 'ativo'])


class ObjetivoPDI(models.Model):
    """Modelo que representa os Objetivos do Plano de Desenvolvimento Institucional (PDI)."""
    desafio = models.ForeignKey(DesafioPDI, on_delete=models.CASCADE, related_name='objetivos')
    codigo = models.CharField(max_length=20)
    descricao = models.CharField(max_length=300)
    ativo = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Metadados de configuração para o modelo ObjetivoPDI."""
        verbose_name = 'Objetivo PDI'
        verbose_name_plural = 'Objetivos PDI'
        ordering = ['codigo']

    def __str__(self):
        """Retorna a representação textual do objeto em formato string."""
        return f"Objetivo {self.codigo} - {str(self.descricao)[:50]}"

    def soft_delete(self):
        """Realiza a exclusão lógica do registro definindo a data de deleção."""
        self.deleted_at = timezone.now()
        self.ativo = False
        self.save(update_fields=['deleted_at', 'ativo'])

class Macroprocesso(models.Model):
    """Modelo que representa os Macroprocessos do Plano de Desenvolvimento Institucional (PDI)."""
    nome = models.CharField(max_length=200)
    desafio = models.ForeignKey(
        DesafioPDI,
        on_delete=models.SET_NULL,
        related_name='macroprocessos',
        null=True,
        blank=True
    )
    ativo = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Metadados de configuração para o modelo Macroprocesso."""
        verbose_name = 'Macroprocesso'
        verbose_name_plural = 'Macroprocessos'
        ordering = ['nome']

    def __str__(self):
        """Retorna a representação textual do objeto em formato string."""
        return f"{self.nome}"

    def soft_delete(self):
        """Realiza a exclusão lógica do registro definindo a data de deleção."""
        self.deleted_at = timezone.now()
        self.ativo = False
        self.save(update_fields=['deleted_at', 'ativo'])
