'''Modelos do banco de dados dos riscos'''

from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from organizacional.models import Setor
from configuracao.models import Macroprocesso, ObjetivoPDI


class PlanoDeRisco(models.Model):
    '''model do plano de risco'''
    STATUS_SEM_TRATAMENTO = 'sem_tratamento'
    STATUS_COM_TRATAMENTO = 'com_tratamento'
    STATUS_CHOICES = [
        (STATUS_SEM_TRATAMENTO, 'Sem Tratamento'),
        (STATUS_COM_TRATAMENTO, 'Com Tratamento'),
    ]

    setor           = models.ForeignKey(Setor, on_delete=models.PROTECT,
                                        related_name='planos')
    criado_por      = models.ForeignKey(settings.AUTH_USER_MODEL,
                                        on_delete=models.PROTECT, related_name='planos_criados')
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                       default=STATUS_SEM_TRATAMENTO, db_index=True)
    criado_em       = models.DateTimeField(auto_now_add=True)
    atualizado_em   = models.DateTimeField(auto_now=True)
    deleted_at      = models.DateTimeField(null=True, blank=True)
    history         = HistoricalRecords()

    class Meta:
        verbose_name = 'Plano de Risco'
        verbose_name_plural = 'Planos de Risco'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Plano #{self.pk} — {self.setor} ({self.get_status_display()})'

    def soft_delete(self):
        '''Implementa o soft delete do risco'''
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    @property
    def ativo(self):
        '''se não stiver atio, implementa o soft delete'''
        return self.deleted_at is None


class IdentificacaoRisco(models.Model):
    '''model de identificação de risco'''
    TIPOLOGIA_CHOICES = [
        ('ESTRATEGICO',   'Estratégico'),
        ('OPERACIONAL',   'Operacional'),
        ('INTEGRIDADE',   'Integridade'),
        ('IMAGEM',        'Imagem'),
        ('LEGAL',         'Legal / Conformidade'),
        ('FINANCEIRO',    'Financeiro / Orçamentário'),
        ('AMB_EXTERNO',   'Ambiente Externo'),
    ]

    plano           = models.OneToOneField(PlanoDeRisco,
                                           on_delete=models.CASCADE, related_name='identificacao')
    tipologia       = models.CharField(max_length=20, choices=TIPOLOGIA_CHOICES)
    macroprocesso   = models.ForeignKey(Macroprocesso,
                                        on_delete=models.SET_NULL, null=True, blank=True)
    objetivo_pdi    = models.ForeignKey(ObjetivoPDI,
                                        on_delete=models.SET_NULL, null=True, blank=True)
    descricao_evento = models.TextField('Descrição do Evento de Risco')
    causas          = models.TextField('Causas')
    consequencias   = models.TextField('Consequências')

    class Meta:
        verbose_name = 'Identificação do Risco'


class AvaliacaoRisco(models.Model):
    '''model do avaliação de risco'''
    PROBABILIDADE_CHOICES = [
        (1, '1 — Muito Baixa'),
        (2, '2 — Baixa'),
        (3, '3 — Média'),
        (4, '4 — Alta'),
        (5, '5 — Muito Alta'),
    ]
    IMPACTO_CHOICES = [
        (1, '1 — Muito Baixo'),
        (2, '2 — Baixo'),
        (3, '3 — Médio'),
        (4, '4 — Alto'),
        (5, '5 — Muito Alto'),
    ]
    EFICACIA_CHOICES = [
        ('INEXISTENTE',  'Inexistente'),
        ('FRACO',        'Fraco'),
        ('MEDIANO',      'Mediano'),
        ('SATISFATORIO', 'Satisfatório'),
        ('FORTE',        'Forte'),
    ]
    FATOR_EFICACIA = {
        'INEXISTENTE': 1.0,
        'FRACO':       0.8,
        'MEDIANO':     0.6,
        'SATISFATORIO': 0.4,
        'FORTE':       0.2,
    }
    NIVEL_CHOICES = [
        ('BAIXO',    'Baixo'),
        ('MODERADO', 'Moderado'),
        ('ALTO',     'Alto'),
        ('EXTREMO',  'Extremo'),
    ]

    plano               = models.OneToOneField(PlanoDeRisco,
                                               on_delete=models.CASCADE, related_name='avaliacao')
    probabilidade       = models.PositiveSmallIntegerField(choices=PROBABILIDADE_CHOICES)
    impacto             = models.PositiveSmallIntegerField(choices=IMPACTO_CHOICES)
    risco_inerente      = models.PositiveSmallIntegerField(editable=False, default=0)
    nivel_inerente      = models.CharField(max_length=10,
                                           choices=NIVEL_CHOICES, editable=False, blank=True)
    eficacia_controles  = models.CharField(max_length=15,
                                           choices=EFICACIA_CHOICES)
    descricao_controles = models.TextField('Descrição dos Controles Internos', blank=True)
    risco_residual      = models.FloatField(editable=False, default=0)
    nivel_residual      = models.CharField(max_length=10,
                                           choices=NIVEL_CHOICES, editable=False, blank=True)

    class Meta:
        verbose_name = 'Avaliação do Risco'

    @staticmethod
    def calcular_nivel(valor):
        '''calcula o nível de periculosidade do risco'''
        if valor < 4:
            return 'BAIXO'
        if valor < 12:
            return 'MODERADO'
        if valor < 20:
            return 'ALTO'
        return 'EXTREMO'

    def save(self, *args, **kwargs):
        self.risco_inerente = self.probabilidade * self.impacto
        self.nivel_inerente = self.calcular_nivel(self.risco_inerente)
        fator = self.FATOR_EFICACIA.get(self.eficacia_controles, 1.0)
        self.risco_residual = round(self.risco_inerente * fator, 2) \
                                    if 'round' in dir() \
                                    else round(self.risco_inerente * fator, 2)
        self.nivel_residual = self.calcular_nivel(self.risco_residual)
        super().save(*args, **kwargs)


class TratamentoRisco(models.Model):
    '''Define os atributos do tratamento do risco.
    Bem dizer opcional'''
    RESPOSTA_CHOICES = [
        ('MITIGAR',    'Mitigar'),
        ('TRANSFERIR', 'Transferir'),
        ('EVITAR',     'Evitar'),
        ('ACEITAR',    'Aceitar'),
    ]
    TIPO_ACAO_CHOICES = [
        ('PREVENTIVA',    'Preventiva'),
        ('CORRETIVA',     'Corretiva'),
        ('COMPENSATORIA', 'Compensatória'),
    ]
    SITUACAO_CHOICES = [
        ('NAO_INICIADO', 'Não Iniciado'),
        ('EM_EXECUCAO',  'Em Execução'),
        ('CONCLUIDO',    'Concluído'),
        ('ATRASADO',     'Atrasado'),
    ]

    plano                   = models.OneToOneField(PlanoDeRisco,
                                                   on_delete=models.CASCADE,
                                                   related_name='tratamento')
    resposta                = models.CharField(max_length=15, choices=RESPOSTA_CHOICES)
    tipo_acao               = models.CharField(max_length=15, choices=TIPO_ACAO_CHOICES)
    descricao_acao          = models.TextField('Descrição da Ação')
    situacao                = models.CharField(max_length=15,
                                                choices=SITUACAO_CHOICES, default='NAO_INICIADO')
    data_inicio             = models.DateField(null=True, blank=True)
    data_conclusao_prevista = models.DateField(null=True, blank=True)
    responsavel             = models.CharField(max_length=200)
    parceiros               = models.TextField(blank=True)
    observacoes             = models.TextField(blank=True)
    resultados_observados   = models.TextField(blank=True)
    analise_critica         = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tratamento do Risco'
