"""Cria planos de risco de demonstracao para apresentacao e testes."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from configuracao.models import DesafioPDI, Macroprocesso, ObjetivoPDI
from organizacional.models import Setor, Unidade
from riscos.models import (
    AvaliacaoRisco,
    IdentificacaoRisco,
    PlanoDeRisco,
    TratamentoRisco,
)


class Command(BaseCommand):
    help = 'Cria 50 planos de risco de demonstracao sem duplicar registros existentes.'

    def handle(self, *args, **options):
        usuario = self._usuario_responsavel()
        setores = self._setores_disponiveis()
        desafios = list(DesafioPDI.objects.filter(ativo=True, deleted_at__isnull=True))
        objetivos = list(ObjetivoPDI.objects.filter(ativo=True, deleted_at__isnull=True))
        macros = list(Macroprocesso.objects.filter(ativo=True, deleted_at__isnull=True))

        criados = 0
        ignorados = 0
        atualizados = 0

        with transaction.atomic():
            for indice, dados in enumerate(self._dados_demo(), start=1):
                descricao = f"[DEMO {indice:02d}] {dados['evento']}"
                setor = setores[(indice - 1) % len(setores)]
                identificacao_existente = (
                    IdentificacaoRisco.objects
                    .select_related('plano')
                    .filter(
                        descricao_evento=descricao,
                        plano__deleted_at__isnull=True,
                    )
                    .first()
                )

                if identificacao_existente:
                    plano = identificacao_existente.plano
                    if plano.setor_id != setor.id:
                        plano.setor = setor
                        plano.save(update_fields=['setor'])
                        atualizados += 1
                    ignorados += 1
                    continue

                plano = PlanoDeRisco.objects.create(
                    setor=setor,
                    criado_por=usuario,
                    status=PlanoDeRisco.STATUS_SEM_TRATAMENTO,
                )

                IdentificacaoRisco.objects.create(
                    plano=plano,
                    tipologia=dados['tipologia'],
                    macroprocesso=macros[(indice - 1) % len(macros)] if macros else None,
                    objetivo_pdi=objetivos[(indice - 1) % len(objetivos)] if objetivos else None,
                    desafio_pdi=desafios[(indice - 1) % len(desafios)] if desafios else None,
                    descricao_evento=descricao,
                    causas=dados['causas'],
                    consequencias=dados['consequencias'],
                )

                AvaliacaoRisco.objects.create(
                    plano=plano,
                    probabilidade=dados['probabilidade'],
                    impacto=dados['impacto'],
                    eficacia_controles=dados['eficacia'],
                    descricao_controles=dados['controles'],
                )

                if dados['tratamento']:
                    TratamentoRisco.objects.create(
                        plano=plano,
                        resposta=dados['resposta'],
                        tipo_acao=dados['tipo_acao'],
                        descricao_acao=dados['acao'],
                        situacao=dados['situacao'],
                        data_inicio=dados['data_inicio'],
                        data_conclusao_prevista=dados['data_fim'],
                        responsavel=dados['responsavel'],
                        parceiros=dados['parceiros'],
                        observacoes=dados['observacoes'],
                        resultados_observados=dados['resultados'],
                        analise_critica=dados['analise'],
                    )
                    plano.status = PlanoDeRisco.STATUS_COM_TRATAMENTO
                    plano.save(update_fields=['status'])

                criados += 1

        self.stdout.write(self.style.SUCCESS(f'Planos criados: {criados}'))
        self.stdout.write(f'Planos ignorados por ja existirem: {ignorados}')
        self.stdout.write(f'Planos redistribuidos entre unidades: {atualizados}')
        self.stdout.write(
            'Para testar notificacoes de atraso, rode: python manage.py verificar_atrasos'
        )

    def _usuario_responsavel(self):
        Usuario = get_user_model()
        usuario = (
            Usuario.objects.filter(is_superuser=True).first()
            or Usuario.objects.filter(perfil='ADMIN').first()
            or Usuario.objects.first()
        )
        if not usuario:
            raise CommandError(
                'Nenhum usuario encontrado. Crie um administrador antes de rodar o seed.'
            )
        return usuario

    def _setores_disponiveis(self):
        estrutura = [
            (
                'PROGRAD',
                'Pro-Reitoria de Graduacao',
                'PRO_REITORIA',
                [
                    ('Coordenadoria de Ensino', 'ENS'),
                    ('Coordenadoria de Projetos Pedagogicos', 'CPP'),
                    ('Secretaria Academica', 'SEC'),
                ],
            ),
            (
                'CT',
                'Centro de Tecnologia',
                'CENTRO',
                [
                    ('Departamento de Informatica', 'INF'),
                    ('Departamento de Eletricidade', 'ELE'),
                    ('Laboratorio de Inovacao', 'LAB'),
                ],
            ),
            (
                'CCSH',
                'Centro de Ciencias Sociais e Humanas',
                'CENTRO',
                [
                    ('Departamento de Administracao', 'ADM'),
                    ('Nucleo de Apoio a Pesquisa', 'NAP'),
                ],
            ),
            (
                'REITO',
                'Reitoria',
                'REITORIA',
                [
                    ('Gabinete do Reitor', 'GAB'),
                    ('Assessoria de Planejamento', 'PLAN'),
                ],
            ),
            (
                'PRA',
                'Pro-Reitoria de Administracao',
                'PRO_REITORIA',
                [
                    ('Departamento de Compras', 'COMP'),
                    ('Departamento de Patrimonio', 'PAT'),
                ],
            ),
            (
                'CPD',
                'Centro de Processamento de Dados',
                'ORGAO',
                [
                    ('Infraestrutura e Redes', 'REDES'),
                    ('Sistemas Institucionais', 'SIS'),
                ],
            ),
        ]

        setores_demo = []
        for sigla_unidade, nome_unidade, tipo, setores in estrutura:
            unidade, _ = Unidade.objects.get_or_create(
                sigla=sigla_unidade,
                defaults={
                    'nome': nome_unidade,
                    'tipo': tipo,
                    'ativo': True,
                },
            )
            for nome_setor, sigla_setor in setores:
                setor, _ = Setor.objects.get_or_create(
                    unidade=unidade,
                    nome=nome_setor,
                    defaults={'sigla': sigla_setor, 'ativo': True},
                )
                setores_demo.append(setor)

        setores_existentes = list(
            Setor.objects
            .filter(ativo=True, deleted_at__isnull=True)
            .exclude(id__in=[setor.id for setor in setores_demo])
            .select_related('unidade')
        )
        return setores_demo + setores_existentes

    def _dados_demo(self):
        hoje = timezone.localdate()
        eventos = [
            (
                'Atraso na analise e aprovacao de propostas academicas.',
                'OPERACIONAL', 3, 4, 'MEDIANO',
                'Documentacao incompleta e ausencia de procedimento padronizado.',
                'Perda de prazos, retrabalho e atraso no inicio dos projetos.',
            ),
            (
                'Falha na atualizacao de dados dos setores no sistema.',
                'OPERACIONAL', 2, 3, 'SATISFATORIO',
                'Comunicacao descentralizada e baixa frequencia de revisao.',
                'Indicadores gerenciais podem ficar desatualizados.',
            ),
            (
                'Indisponibilidade temporaria do sistema em periodo critico.',
                'OPERACIONAL', 4, 5, 'FRACO',
                'Infraestrutura limitada e ausencia de monitoramento continuo.',
                'Interrupcao de cadastros e impacto no acompanhamento dos riscos.',
            ),
            (
                'Divulgacao incompleta de orientacoes sobre gestao de riscos.',
                'IMAGEM', 3, 3, 'MEDIANO',
                'Materiais institucionais dispersos e falta de rotina de comunicacao.',
                'Baixa adesao dos setores e percepcao negativa do processo.',
            ),
            (
                'Registro incorreto de probabilidade e impacto dos riscos.',
                'OPERACIONAL', 3, 4, 'SATISFATORIO',
                'Falta de capacitacao e interpretacao diferente da matriz.',
                'Classificacao inadequada e priorizacao equivocada dos tratamentos.',
            ),
            (
                'Descumprimento de prazo em plano de tratamento de risco.',
                'LEGAL', 4, 4, 'FRACO',
                'Ausencia de acompanhamento periodico e responsaveis sobrecarregados.',
                'Plano fica vencido e aumenta a exposicao institucional.',
            ),
            (
                'Perda de historico de decisoes sobre tratamento de riscos.',
                'INTEGRIDADE', 2, 4, 'MEDIANO',
                'Registros feitos fora do sistema e falta de centralizacao.',
                'Dificuldade de auditoria e perda de rastreabilidade.',
            ),
            (
                'Divergencia entre setores sobre responsavel pelo tratamento.',
                'OPERACIONAL', 3, 3, 'MEDIANO',
                'Papéis pouco definidos e dependencias entre unidades.',
                'Acoes ficam paradas e o risco permanece sem mitigacao.',
            ),
            (
                'Aumento de custos por falha no planejamento de compras.',
                'FINANCEIRO', 3, 5, 'FRACO',
                'Estimativas incompletas e atraso na consolidacao de demandas.',
                'Necessidade de remanejamento orcamentario e perda de economicidade.',
            ),
            (
                'Nao conformidade em processo administrativo sensivel.',
                'LEGAL', 2, 5, 'MEDIANO',
                'Mudancas normativas nao incorporadas ao fluxo interno.',
                'Risco de apontamentos de auditoria e necessidade de correcao formal.',
            ),
        ]

        tratamentos = [
            True, True, True, True, False, True, True, False, True, True,
            True, True, False, True, True, True, True, False, True, True,
            True, True, True, False, True, True, True, True, False, True,
            True, True, False, True, True, True, False, True, True, True,
            True, False, True, True, True, True, False, True, True, True,
        ]
        respostas = ['MITIGAR', 'MITIGAR', 'EVITAR', 'TRANSFERIR', 'ACEITAR']
        tipos_acao = ['PREVENTIVA', 'CORRETIVA', 'COMPENSATORIA']
        situacoes = ['NAO_INICIADO', 'EM_EXECUCAO', 'CONCLUIDO']

        dados = []
        for indice in range(50):
            evento, tipologia, prob, impacto, eficacia, causas, consequencias = (
                eventos[indice % len(eventos)]
            )
            vencido = indice in {0, 5, 8, 11, 17, 23, 28}
            data_inicio = hoje - timedelta(days=40 - indice)
            data_fim = hoje - timedelta(days=indice % 12 + 1) if vencido else (
                hoje + timedelta(days=10 + indice)
            )
            situacao = 'EM_EXECUCAO' if vencido else situacoes[indice % len(situacoes)]

            dados.append({
                'evento': evento,
                'tipologia': tipologia,
                'probabilidade': max(1, min(5, prob + (indice % 3) - 1)),
                'impacto': max(1, min(5, impacto + (indice % 2))),
                'eficacia': eficacia,
                'causas': causas,
                'consequencias': consequencias,
                'controles': (
                    'Revisao periodica, registro formal das acoes e acompanhamento '
                    'pela chefia imediata.'
                ),
                'tratamento': tratamentos[indice],
                'resposta': respostas[indice % len(respostas)],
                'tipo_acao': tipos_acao[indice % len(tipos_acao)],
                'acao': (
                    'Definir responsavel, revisar o fluxo de trabalho, registrar '
                    'evidencias e acompanhar o prazo ate a conclusao.'
                ),
                'situacao': situacao,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'responsavel': f'Responsavel Demo {indice + 1}',
                'parceiros': 'Setor demandante; equipe administrativa; chefia imediata.',
                'observacoes': 'Registro criado para demonstracao do sistema.',
                'resultados': 'Acompanhamento em andamento.',
                'analise': 'A efetividade sera reavaliada apos a conclusao da acao.',
            })

        return dados
