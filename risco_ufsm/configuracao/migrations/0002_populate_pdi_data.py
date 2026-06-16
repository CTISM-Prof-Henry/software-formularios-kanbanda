"""Migration de dados: popula Desafios PDI, Objetivos PDI e Macroprocessos
conforme o Guia de Aplicação da UFSM (PDI 2016-2026)."""

from django.db import migrations


DESAFIOS = [
    (1, 'Internacionalização'),
    (2, 'Educação inovadora e transformadora com excelência acadêmica'),
    (3, 'Inclusão Social'),
    (4, 'Inovação, geração de conhecimento e transferência de tecnologia'),
    (5, 'Modernização e desenvolvimento organizacional'),
    (6, 'Desenvolvimento local, regional e nacional'),
    (7, 'Gestão ambiental'),
]

# (codigo, descricao, numero_desafio)
OBJETIVOS = [
    ('PR-D1-02', 'Oportunizar experiências de internacionalização aos alunos.', 1),
    ('PR-D1-03', 'Firmar relações de colaboração internacional para trocas culturais e políticas acadêmicas e de gestão.', 1),
    ('PR-D2-01', 'Fortalecer o aprendizado extra-classe, oportunizando atividades de extensão, inserção social, empreendedorismo, pesquisa e inovação.', 2),
    ('PR-D2-02', 'Manter métodos de ensino atualizados e de acordo com as expectativas dos alunos.', 2),
    ('PR-D2-03', 'Possuir currículos interdisciplinares, flexíveis e atualizados em relação às demandas da sociedade.', 2),
    ('PR-D2-04', 'Desenvolver estratégias de permanência que incentivem o aprendizado e a conclusão do curso em prazo adequado.', 2),
    ('AI-D2-01', 'Manter um quadro docente capacitado quanto ao uso de práticas pedagógicas.', 2),
    ('AI-D2-02', 'Desenvolver uma cultura de comprometimento organizacional.', 2),
    ('AI-D2-03', 'Oferecer uma infraestrutura de apoio qualificada e de acordo com as necessidades de cada área de conhecimento.', 2),
    ('AI-D2-04', 'Fortalecer a cultura de inovação, compromisso social e integração ensino-pesquisa-extensão e entre as áreas do conhecimento.', 2),
    ('AS-D2-01', 'Oferecer cursos de excelência integrados à sociedade.', 2),
    ('AS-D2-02', 'Formar alunos com visão global e humanista, comprometidos com sociedade, meio ambiente e desenvolvimento científico e tecnológico.', 2),
    ('AS-D2-03', 'Estimular o sentimento de pertencimento e satisfação dos alunos para com a UFSM.', 2),
    ('AI-D3-01', 'Preparar o corpo técnico e docente para lidar com os diferentes aspectos da inclusão social.', 3),
    ('AI-D3-02', 'Disseminar uma cultura ética em relação à inclusão, diversidade e meio ambiente.', 3),
    ('AS-D3-01', 'Fortalecer as políticas de acesso à universidade em consonância com ações afirmativas.', 3),
    ('PR-D3-01', 'Fortalecer as políticas de assistência estudantil focadas na permanência, conclusão e bom uso dos recursos.', 3),
    ('AI-D4-01', 'Estimular o desenvolvimento de um quadro docente com pesquisadores de excelência que sejam referência.', 4),
    ('AI-D4-02', 'Equipar laboratórios de pesquisa conforme necessidades de cada área e uso multiusuário.', 4),
    ('AI-D4-03', 'Expandir os ambientes de inovação.', 4),
    ('AS-D4-01', 'Aumentar a inserção científica institucional.', 4),
    ('AS-D4-02', 'Fortalecer a inovação, o desenvolvimento tecnológico e a transferência de tecnologias para a sociedade.', 4),
    ('AS-D4-03', 'Desenvolver e inserir na sociedade tecnologias sociais e arte & cultura.', 4),
    ('PR-D4-02', 'Implementar projetos interdisciplinares.', 4),
    ('AI-D5-01', 'Possuir infraestrutura de engenharia e logística adequada, com acessibilidade e respeito ambiental.', 5),
    ('AI-D5-02', 'Desenvolver competências gerenciais, técnicas e de liderança para manter excelência.', 5),
    ('AI-D5-03', 'Modernizar infraestrutura de TI para suportar necessidades acadêmicas e administrativas.', 5),
    ('AI-D5-04', 'Desenvolver sistema de seleção e progressão docente equilibrando ensino, pesquisa, extensão e particularidades de áreas e níveis.', 5),
    ('AS-D5-01', 'Fortalecer políticas de governança, transparência e profissionalização da gestão.', 5),
    ('PR-D5-01', 'Otimizar rotinas administrativas e sistemas de informação, com agilidade, transparência e qualidade.', 5),
    ('PR-D5-02', 'Adequar a estrutura administrativa com estratégia de alocação e dimensionamento de pessoal.', 5),
    ('PR-D5-03', 'Aumentar eficiência da comunicação institucional.', 5),
    ('PR-D5-04', 'Desenvolver processos e rotinas de trabalho considerando realidade multicampi e níveis de ensino.', 5),
    ('SF-D5-01', 'Aumentar orçamento federal recebido.', 5),
    ('SF-D5-02', 'Incrementar captação de recursos extra-orçamentários.', 5),
    ('SF-D5-03', 'Desenvolver gestão orçamentária transparente, eficiente e alinhada à estratégia institucional.', 5),
    ('AS-D6-01', 'Desenvolver projetos relacionados a políticas públicas nas áreas saúde, educação, inclusão, gestão ambiental etc.', 6),
    ('AS-D6-02', 'Oferecer serviços de apoio à comunidade em consonância com política de inovação e extensão universitária.', 6),
    ('AS-D6-03', 'Desenvolver projetos de extensão com foco na intervenção, transformação e desenvolvimento social.', 6),
    ('PR-D6-01', 'Fomentar projetos de pesquisa aplicados a problemas sociais e universitários.', 6),
    ('PR-D6-02', 'Instituir processo de relacionamento e colaboração com os diversos setores da sociedade.', 6),
    ('AS-D7-01', 'Implantar um sistema de gestão ambiental.', 7),
    ('PR-D7-01', 'Manter processos e rotinas que valorizem os aspectos da gestão ambiental.', 7),
]

MACROPROCESSOS = [
    'Assistência Estudantil',
    'Compras, Suprimentos e Patrimônio',
    'Comunicação Institucional',
    'Controle Ambiental',
    'Controle Bibliográfico e Editorial',
    'Documentos',
    'Ensino',
    'Extensão',
    'Inclusão Social',
    'Infraestrutura de Pesquisa e Inovação',
    'Infraestrutura dos Campi',
    'Inovação e Empreendedorismo',
    'Orçamento e Finanças',
    'Pesquisa',
    'Pesquisa Institucional',
    'Pessoas',
    'Planejamento Acadêmico',
    'Planejamento Pedagógico',
    'Projetos Acadêmicos',
    'Registro e Controle Acadêmico',
    'Relações Institucionais',
    'Tecnologia da Informação',
]


def populate(apps, schema_editor):
    DesafioPDI = apps.get_model('configuracao', 'DesafioPDI')
    ObjetivoPDI = apps.get_model('configuracao', 'ObjetivoPDI')
    Macroprocesso = apps.get_model('configuracao', 'Macroprocesso')

    # Desafios
    desafio_map = {}
    for numero, descricao in DESAFIOS:
        obj, _ = DesafioPDI.objects.get_or_create(
            numero=numero,
            defaults={'descricao': descricao, 'ativo': True},
        )
        desafio_map[numero] = obj

    # Objetivos
    for codigo, descricao, num_desafio in OBJETIVOS:
        ObjetivoPDI.objects.get_or_create(
            codigo=codigo,
            defaults={
                'descricao': descricao,
                'desafio': desafio_map[num_desafio],
                'ativo': True,
            },
        )

    # Macroprocessos (sem vínculo de desafio — campo opcional no modelo)
    for nome in MACROPROCESSOS:
        Macroprocesso.objects.get_or_create(
            nome=nome,
            defaults={'ativo': True},
        )


def depopulate(apps, schema_editor):
    """Reversão: remove apenas os registros criados por esta migration."""
    DesafioPDI = apps.get_model('configuracao', 'DesafioPDI')
    ObjetivoPDI = apps.get_model('configuracao', 'ObjetivoPDI')
    Macroprocesso = apps.get_model('configuracao', 'Macroprocesso')

    codigos = [c for c, _, __ in OBJETIVOS]
    ObjetivoPDI.objects.filter(codigo__in=codigos).delete()

    numeros = [n for n, _ in DESAFIOS]
    DesafioPDI.objects.filter(numero__in=numeros).delete()

    nomes = MACROPROCESSOS
    Macroprocesso.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate, depopulate),
    ]