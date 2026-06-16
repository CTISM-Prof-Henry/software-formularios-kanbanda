"""Geração do relatório PDF dos planos de risco usando ReportLab."""

from io import BytesIO
from html import escape

from django.conf import settings
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


CORES_NIVEL = {
    'BAIXO': colors.HexColor('#2ecc71'),
    'MODERADO': colors.HexColor('#f39c12'),
    'ALTO': colors.HexColor('#e67e22'),
    'EXTREMO': colors.HexColor('#e74c3c'),
}


def _texto(valor):
    """Converte valores vazios para hifen e protege textos do Paragraph."""
    if valor is None or valor == '':
        return '-'
    return escape(str(valor)).replace('\n', '<br/>')


def _data(valor):
    if not valor:
        return '-'
    return valor.strftime('%d/%m/%Y')


def _paragrafo(valor, estilo):
    return Paragraph(_texto(valor), estilo)


def _linha(rotulo, valor, estilos):
    return [
        Paragraph(f'<b>{escape(rotulo)}</b>', estilos['Campo']),
        _paragrafo(valor, estilos['Normal']),
    ]


def _tabela_linhas(linhas):
    tabela = Table(linhas, colWidths=[4.2 * cm, 11.8 * cm])
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#999999')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f3f6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return tabela


def _badge(texto, nivel, estilos):
    cor = CORES_NIVEL.get(nivel, colors.HexColor('#777777'))
    return Table(
        [[Paragraph(f'<font color="white"><b>{escape(texto)}</b></font>', estilos['Badge'])]],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cor),
            ('BOX', (0, 0), (-1, -1), 0.25, cor),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]),
    )


def _risco_com_badge(valor, nivel, texto_nivel, estilos):
    return Table(
        [[Paragraph(f'<b>{_texto(valor)}</b>', estilos['Normal']), _badge(texto_nivel, nivel, estilos)]],
        colWidths=[1.3 * cm, 3.0 * cm],
        style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]),
    )


def _secao(titulo, elementos, estilos):
    elementos.append(Spacer(1, 0.35 * cm))
    elementos.append(Paragraph(titulo, estilos['Secao']))


def _objeto_relacionado(plano, nome):
    try:
        return getattr(plano, nome)
    except AttributeError:
        return None


def gerar_plano_pdf(plano):
    """Retorna os bytes do PDF de um plano de risco."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
        title=f'Plano de Risco #{plano.pk}',
    )

    base = getSampleStyleSheet()
    estilos = {
        'Normal': ParagraphStyle(
            'PDFNormal',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
        ),
        'Campo': ParagraphStyle(
            'PDFCampo',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=13,
        ),
        'Instituicao': ParagraphStyle(
            'PDFInstituicao',
            parent=base['Normal'],
            alignment=TA_RIGHT,
            fontSize=9,
            leading=12,
        ),
        'Titulo': ParagraphStyle(
            'PDFTitulo',
            parent=base['Title'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#173b62'),
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
        ),
        'Subtitulo': ParagraphStyle(
            'PDFSubtitulo',
            parent=base['Normal'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#555555'),
            fontSize=8.5,
            leading=11,
        ),
        'Secao': ParagraphStyle(
            'PDFSecao',
            parent=base['Heading2'],
            textColor=colors.HexColor('#1f4e79'),
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=15,
            spaceAfter=6,
        ),
        'Badge': ParagraphStyle(
            'PDFBadge',
            parent=base['Normal'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
        ),
        'Vazio': ParagraphStyle(
            'PDFVazio',
            parent=base['Italic'],
            textColor=colors.HexColor('#777777'),
            fontSize=9.5,
            leading=13,
        ),
    }

    elementos = []
    logo_path = settings.BASE_DIR / 'riscos' / 'assets' / 'ufsm-logo.png'

    if logo_path.exists():
        logo = Image(str(logo_path), width=4.2 * cm, height=1.4 * cm, kind='proportional')
    else:
        logo = Paragraph('<b>UFSM</b>', estilos['Titulo'])

    cabecalho = Table(
        [[
            logo,
            Paragraph(
                '<b>UNIVERSIDADE FEDERAL DE SANTA MARIA</b><br/>'
                'Sistema de Gestão de Riscos Institucionais<br/>'
                'Relatório de gerenciamento de riscos',
                estilos['Instituicao'],
            ),
        ]],
        colWidths=[6.2 * cm, 9.8 * cm],
    )
    cabecalho.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
    ]))
    elementos.append(cabecalho)

    titulo = Table(
        [
            [
            Paragraph('PLANO DE ANÁLISE DE RISCO', estilos['Titulo']),
            ],
            [
            Paragraph('Identificação, avaliação, tratamento e monitoramento', estilos['Subtitulo']),
            ],
        ],
        colWidths=[16 * cm],
    )
    titulo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f6f9')),
        ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor('#1f4e79')),
        ('LINEBELOW', (0, 0), (-1, -1), 1.5, colors.HexColor('#1f4e79')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    elementos.append(titulo)
    elementos.append(Spacer(1, 0.2 * cm))

    metadados = Table(
        [[
            Paragraph(f'<b>Plano:</b> nº {plano.pk}', estilos['Normal']),
            Paragraph(f'<b>Setor:</b> {_texto(plano.setor)}', estilos['Normal']),
            Paragraph(f'<b>Emissão:</b> {timezone.localtime().strftime("%d/%m/%Y %H:%M")}', estilos['Normal']),
        ]],
        colWidths=[3.5 * cm, 8.2 * cm, 4.3 * cm],
    )
    metadados.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#c8cdd2')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elementos.append(metadados)

    identificacao = _objeto_relacionado(plano, 'identificacao')
    avaliacao = _objeto_relacionado(plano, 'avaliacao')
    tratamento = _objeto_relacionado(plano, 'tratamento')

    _secao('1. Identificação e Análise', elementos, estilos)
    elementos.append(_tabela_linhas([
        _linha('Tipologia', identificacao.get_tipologia_display() if identificacao else '-', estilos),
        _linha('Macroprocesso', identificacao.macroprocesso if identificacao else '-', estilos),
        _linha('Objetivo PDI', identificacao.objetivo_pdi if identificacao else '-', estilos),
        _linha('Desafio PDI', identificacao.desafio_pdi if identificacao else '-', estilos),
        _linha('Evento de risco', identificacao.descricao_evento if identificacao else '-', estilos),
        _linha('Causas', identificacao.causas if identificacao else '-', estilos),
        _linha('Consequências', identificacao.consequencias if identificacao else '-', estilos),
    ]))

    _secao('2. Avaliação', elementos, estilos)
    if avaliacao:
        elementos.append(_tabela_linhas([
            _linha('Probabilidade', avaliacao.get_probabilidade_display(), estilos),
            _linha('Impacto', avaliacao.get_impacto_display(), estilos),
            [
                Paragraph('<b>Risco inerente</b>', estilos['Campo']),
                _risco_com_badge(
                    avaliacao.risco_inerente,
                    avaliacao.nivel_inerente,
                    avaliacao.get_nivel_inerente_display(),
                    estilos,
                ),
            ],
            _linha('Controles internos', avaliacao.descricao_controles, estilos),
            _linha('Eficácia dos controles', avaliacao.get_eficacia_controles_display(), estilos),
            [
                Paragraph('<b>Risco residual</b>', estilos['Campo']),
                _risco_com_badge(
                    avaliacao.risco_residual,
                    avaliacao.nivel_residual,
                    avaliacao.get_nivel_residual_display(),
                    estilos,
                ),
            ],
        ]))
    else:
        elementos.append(Paragraph('Este plano ainda não possui avaliação cadastrada.', estilos['Vazio']))

    _secao('3. Tratamento', elementos, estilos)
    if tratamento:
        elementos.append(_tabela_linhas([
            _linha('Resposta ao risco', tratamento.get_resposta_display(), estilos),
            _linha('Tipo de ação', tratamento.get_tipo_acao_display(), estilos),
            _linha('Descrição da ação', tratamento.descricao_acao, estilos),
            _linha('Responsavel', tratamento.responsavel, estilos),
            _linha('Parceiros', tratamento.parceiros, estilos),
            _linha('Data de início', _data(tratamento.data_inicio), estilos),
            _linha('Conclusão prevista', _data(tratamento.data_conclusao_prevista), estilos),
            _linha('Situação', tratamento.get_situacao_display(), estilos),
            _linha('Observações', tratamento.observacoes, estilos),
            _linha('Resultados observados', tratamento.resultados_observados, estilos),
            _linha('Análise crítica', tratamento.analise_critica, estilos),
        ]))
    else:
        elementos.append(Paragraph('Este plano ainda não possui tratamento cadastrado.', estilos['Vazio']))

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
