"""CRUD completo de planos de risco."""

import json

from django.db import transaction
from django.db.models import Q, Count
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.template.loader import render_to_string

from accounts.decorators import requer_admin
from organizacional.models import Setor, Unidade, UsuarioSetor

from .services import qs_planos, pode_editar
from .models import PlanoDeRisco, AvaliacaoRisco, IdentificacaoRisco, Notificacao
from .forms import IdentificacaoForm, AvaliacaoForm, TratamentoForm, RemanejarForm

# Valores do campo perfil no modelo de usuário — devem ser idênticos aos de
# accounts.models.Perfil (TextChoices), que usa valores em maiúsculas.
PERFIL_ADMINISTRADOR = 'ADMIN'
PERFIL_GESTOR_UNIDADE = 'GESTOR_UNIDADE'
PERFIL_GESTOR_SETOR = 'GESTOR_SETOR'
PERFIL_SERVIDOR = 'SERVIDOR'


def _setor_qs_para_usuario(user):
    """
    Retorna o queryset de Setor disponível para seleção conforme perfil:
      - Administrador / is_superuser: todos os setores ativos.
      - Gestor da Unidade: todos os setores das unidades a que pertence.
      - Gestor de Setor: apenas os setores diretamente vinculados ao usuário.
      - Servidor: nenhum (não cria planos).
    """
    base = Setor.objects.filter(deleted_at__isnull=True).select_related('unidade').order_by('nome')
    perfil = getattr(user, 'perfil', '')

    if perfil == PERFIL_ADMINISTRADOR or user.is_superuser:
        return base

    setores_ids = UsuarioSetor.objects.filter(usuario=user).values_list('setor_id', flat=True)

    if perfil == PERFIL_GESTOR_UNIDADE:
        unidades_ids = Setor.objects.filter(id__in=setores_ids).values_list('unidade_id', flat=True)
        return base.filter(unidade_id__in=unidades_ids)

    # gestor_setor: apenas seus setores
    return base.filter(id__in=setores_ids)


@requer_admin
def painel_riscos(request):
    """Visão geral de todos os planos — acesso exclusivo ao Administrador."""
    planos = (
        PlanoDeRisco.objects
        .filter(deleted_at__isnull=True)
        .select_related('setor', 'criado_por')
        .order_by('-criado_em')
    )
    return render(request, 'riscos/painel_riscos.html', {'planos': planos})


@requer_admin
def detalhe_plano(request, pk):
    """Detalhe técnico de um plano — acesso exclusivo ao Administrador."""
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)
    return render(request, 'riscos/detalhe.html', {
        'plano': plano,
        'identificacao': getattr(plano, 'identificacao', None),
        'avaliacao': getattr(plano, 'avaliacao', None),
        'tratamento': getattr(plano, 'tratamento', None),
    })


@login_required
def lista_planos(request):
    """
    Exibe os planos conforme o escopo do usuário (definido por qs_planos).
    Suporta busca por texto livre, filtros por tipologia, nível de risco
    residual e status, e exibe contadores de totais.
    """
    u = request.user
    qs = qs_planos(u)

    total_geral = qs.count()
    total_sem_tratamento = qs.filter(status='sem_tratamento').count()

    busca = request.GET.get('q', '').strip()
    tipologia = request.GET.get('tipologia', '').strip()
    nivel = request.GET.get('nivel', '').strip()
    status = request.GET.get('status', '').strip()

    if busca:
        qs = qs.filter(
            Q(identificacao__tipologia__icontains=busca)
            | Q(identificacao__descricao_evento__icontains=busca)
            | Q(avaliacao__nivel_residual__icontains=busca)
            | Q(setor__nome__icontains=busca)
            | Q(status__icontains=busca)
        )

    # Filtro vindo das células da matriz do dashboard (probabilidade × impacto).
    # Só aplica quando ambos vêm preenchidos e numéricos.
    prob = request.GET.get('probabilidade')
    imp = request.GET.get('impacto')
    if prob and imp and prob.isdigit() and imp.isdigit():
        qs = qs.filter(avaliacao__probabilidade=int(prob),
                       avaliacao__impacto=int(imp))
    if tipologia:
        qs = qs.filter(identificacao__tipologia=tipologia)

    if nivel:
        qs = qs.filter(avaliacao__nivel_residual=nivel)

    if status:
        qs = qs.filter(status=status)

    context = {
        'planos': qs.select_related('setor', 'criado_por',
                                     'identificacao', 'avaliacao').order_by('-criado_em'),
        'total_geral': total_geral,
        'total_sem_tratamento': total_sem_tratamento,
        'busca': busca,
        'filtro_tipologia': tipologia,
        'filtro_nivel': nivel,
        'filtro_status': status,
        'tipologia_choices': IdentificacaoRisco.TIPOLOGIA_CHOICES,
        'nivel_choices': AvaliacaoRisco.NIVEL_CHOICES,
        'status_choices': PlanoDeRisco.STATUS_CHOICES,
    }
    return render(request, 'riscos/lista_planos.html', context)


def _nivel_por_produto(produto):
    """Régua de cor da matriz, espelhando AvaliacaoRisco.calcular_nivel:
    <4 BAIXO, <12 MODERADO, <20 ALTO, senão EXTREMO."""
    if produto < 4:
        return 'BAIXO'
    if produto < 12:
        return 'MODERADO'
    if produto < 20:
        return 'ALTO'
    return 'EXTREMO'


@login_required
def dashboard(request):
    """
    Painel analítico dos planos de risco no escopo do usuário.
    Mostra contadores, distribuição por nível residual, gráficos por
    tipologia e por setor, e a matriz probabilidade × impacto.
    """
    planos = qs_planos(request.user)

    # --- Filtro opcional de unidade (Gestor da Unidade / Admin) ---
    unidade_id = request.GET.get('unidade')
    if unidade_id:
        planos = planos.filter(setor__unidade_id=unidade_id)

    # Lista de unidades para o seletor — só para quem enxerga mais de uma.
    unidades = None
    if request.user.is_admin:
        unidades = Unidade.objects.filter(ativo=True, deleted_at__isnull=True).order_by('nome')
    elif request.user.is_gestor_unidade:
        unidades = request.user.get_unidades_ativas().order_by('nome')

    # --- Contadores gerais ---
    total = planos.count()
    sem_tratamento = planos.filter(status='sem_tratamento').count()
    com_tratamento = planos.filter(status='com_tratamento').count()

    # --- Distribuição por nível residual ---
    avaliacoes = AvaliacaoRisco.objects.filter(plano__in=planos)
    por_nivel = {
        'BAIXO':    avaliacoes.filter(nivel_residual='BAIXO').count(),
        'MODERADO': avaliacoes.filter(nivel_residual='MODERADO').count(),
        'ALTO':     avaliacoes.filter(nivel_residual='ALTO').count(),
        'EXTREMO':  avaliacoes.filter(nivel_residual='EXTREMO').count(),
    }

    # --- Gráfico de rosca por tipologia (Categoria de Risco) ---
    TIPOS = dict(IdentificacaoRisco.TIPOLOGIA_CHOICES)
    por_tipologia = (
        planos.values('identificacao__tipologia')
              .annotate(total=Count('id'))
              .order_by('-total')
    )
    labels_tipologia = [TIPOS.get(item['identificacao__tipologia'], 'Sem tipologia')
                        for item in por_tipologia]
    dados_tipologia = [item['total'] for item in por_tipologia]

    # --- Gráfico de barras por setor (top 10) ---
    por_setor = (
        planos.values('setor__nome')
              .annotate(total=Count('id'))
              .order_by('-total')[:10]
    )
    labels_setor = [item['setor__nome'] for item in por_setor]
    dados_setor = [item['total'] for item in por_setor]

    # --- Matriz probabilidade × impacto ---
    # Decisão técnica: a matriz é pré-montada aqui em Python (uma lista de
    # linhas pronta para iterar), evitando filtros de template com dois
    # argumentos / chaves de tupla, que o Django não suporta.
    contagens = avaliacoes.values('probabilidade', 'impacto').annotate(total=Count('id'))
    mapa = {(c['probabilidade'], c['impacto']): c['total'] for c in contagens}

    siglas_nivel = {
        'BAIXO': 'RB',
        'MODERADO': 'RM',
        'ALTO': 'RA',
        'EXTREMO': 'RE',
    }
    rotulos_impacto = {
        5: '5 - Catastrofico',
        4: '4 - Grande',
        3: '3 - Moderado',
        2: '2 - Pequeno',
        1: '1 - Insignificante',
    }

    matriz = []  # linhas de cima (impacto=5) para baixo (impacto=1)
    for imp in range(5, 0, -1):
        celulas = []
        for prob in range(1, 6):
            nivel = _nivel_por_produto(prob * imp)
            celulas.append({
                'prob': prob,
                'imp': imp,
                'count': mapa.get((prob, imp), 0),
                'nivel': nivel,
                'sigla': siglas_nivel[nivel],
            })
        matriz.append({
            'imp': imp,
            'impacto_rotulo': rotulos_impacto[imp],
            'celulas': celulas,
        })

    # --- Categoria × Nível de Risco (barras empilhadas) ---
    # TIPOS já definido na seção de tipologia.
    NIVEIS = ['EXTREMO', 'ALTO', 'MODERADO', 'BAIXO']
    COR = {'EXTREMO': '#e74c3c', 'ALTO': '#e67e22',
           'MODERADO': '#f39c12', 'BAIXO': '#2ecc71'}
    NOMES_NIVEL = dict(AvaliacaoRisco.NIVEL_CHOICES)

    cn = (planos.values('identificacao__tipologia', 'avaliacao__nivel_residual')
                .annotate(total=Count('id')))
    base = {k: {n: 0 for n in NIVEIS} for k in TIPOS}
    for r in cn:
        t, n = r['identificacao__tipologia'], r['avaliacao__nivel_residual']
        if t in base and n in base[t]:
            base[t][n] = r['total']

    labels_categoria = json.dumps(list(TIPOS.values()), cls=DjangoJSONEncoder)
    datasets_categoria = json.dumps([
        {'label': NOMES_NIVEL[n], 'data': [base[k][n] for k in TIPOS],
         'backgroundColor': COR[n]}
        for n in NIVEIS
    ], cls=DjangoJSONEncoder)

    # --- Riscos por Macroprocesso (um doughnut por macroprocesso) ---
    macros = (planos.values('identificacao__macroprocesso__nome',
                            'avaliacao__nivel_residual')
                    .annotate(total=Count('id')))
    nomes = sorted({(m['identificacao__macroprocesso__nome'] or 'Sem macroprocesso')
                    for m in macros})
    bm = {nome: {n: 0 for n in NIVEIS} for nome in nomes}
    for m in macros:
        nome = m['identificacao__macroprocesso__nome'] or 'Sem macroprocesso'
        n = m['avaliacao__nivel_residual']
        if n in bm[nome]:
            bm[nome][n] = m['total']

    # Uma entrada por macroprocesso → vira um minigráfico no grid.
    # Oculta macroprocessos sem nenhum risco no escopo atual.
    graficos_macro = json.dumps([
        {
            'nome': nome,
            'data': [bm[nome][n] for n in NIVEIS],
            'total': sum(bm[nome].values()),
        }
        for nome in nomes
        if sum(bm[nome].values()) > 0
    ], cls=DjangoJSONEncoder)
    niveis_macro = json.dumps([NOMES_NIVEL[n] for n in NIVEIS], cls=DjangoJSONEncoder)
    cores_macro = json.dumps([COR[n] for n in NIVEIS], cls=DjangoJSONEncoder)

    context = {
        'unidades': unidades,
        'unidade_id': unidade_id,
        'total': total,
        'sem_tratamento': sem_tratamento,
        'com_tratamento': com_tratamento,
        'por_nivel': por_nivel,
        'matriz': matriz,
        'labels_tipologia': json.dumps(labels_tipologia, cls=DjangoJSONEncoder),
        'dados_tipologia': json.dumps(dados_tipologia, cls=DjangoJSONEncoder),
        'labels_setor': json.dumps(labels_setor, cls=DjangoJSONEncoder),
        'dados_setor': json.dumps(dados_setor, cls=DjangoJSONEncoder),
        'labels_categoria': labels_categoria,
        'datasets_categoria': datasets_categoria,
        'graficos_macro': graficos_macro,
        'niveis_macro': niveis_macro,
        'cores_macro': cores_macro,
    }
    return render(request, 'riscos/dashboard.html', context)


@login_required
def novo_plano(request):
    """
    Cria um novo plano de risco em três seções (Identificação, Avaliação,
    Tratamento). A seção de tratamento é opcional no momento da criação.
    Acesso negado para perfil Servidor.
    """
    u = request.user
    if getattr(u, 'perfil', '') == PERFIL_SERVIDOR:
        return HttpResponseForbidden('Servidores não têm permissão para cadastrar planos de risco.')

    setor_qs = _setor_qs_para_usuario(u)

    if request.method == 'POST':
        form_id = IdentificacaoForm(request.POST, setor_qs=setor_qs)
        form_av = AvaliacaoForm(request.POST)
        form_tr = TratamentoForm(request.POST)

        if form_id.is_valid() and form_av.is_valid() and form_tr.is_valid():
            with transaction.atomic():
                # 1. Cria o PlanoDeRisco (cabeçalho)
                plano = PlanoDeRisco.objects.create(
                    setor=form_id.cleaned_data['setor'],
                    criado_por=u,
                    status='sem_tratamento',
                )

                # 2. Salva IdentificacaoRisco vinculado ao plano
                identificacao = form_id.save(commit=False)
                identificacao.plano = plano
                identificacao.save()

                # 3. Salva AvaliacaoRisco — o save() do modelo calcula
                #    risco_inerente, nivel_risco_inerente, risco_residual
                #    e nivel_risco_residual automaticamente
                avaliacao = form_av.save(commit=False)
                avaliacao.plano = plano
                avaliacao.save()

                # 4. Salva TratamentoRisco somente se a seção foi preenchida
                if form_tr.tem_dados():
                    tratamento = form_tr.save(commit=False)
                    tratamento.plano = plano
                    tratamento.save()
                    plano.status = 'com_tratamento'
                    plano.save(update_fields=['status'])

            messages.success(request, 'Plano de risco cadastrado com sucesso.')
            return redirect('riscos:visualizar_plano', pk=plano.pk)

    else:
        form_id = IdentificacaoForm(setor_qs=setor_qs)
        form_av = AvaliacaoForm()
        form_tr = TratamentoForm()

    return render(request, 'riscos/novo_plano.html', {
        'form_identificacao': form_id,
        'form_avaliacao': form_av,
        'form_tratamento': form_tr,
    })


@login_required
def visualizar_plano(request, pk):
    """
    Exibe o plano de risco em modo somente leitura.
    O acesso é verificado pelo escopo de qs_planos: retorna 403 se o
    usuário não tiver permissão de visualização sobre este plano.
    """
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)

    # Verifica se o plano está no escopo do usuário
    if not qs_planos(request.user).filter(pk=plano.pk).exists():
        return HttpResponseForbidden('Você não tem permissão para visualizar este plano.')

    context = {
        'plano': plano,
        'identificacao': getattr(plano, 'identificacao', None),
        'avaliacao': getattr(plano, 'avaliacao', None),
        'tratamento': getattr(plano, 'tratamento', None),
        'pode_editar': pode_editar(plano, request.user),
    }
    return render(request, 'riscos/visualizar_plano.html', context)


@login_required
def gerar_pdf(request, pk):
    """Gera o PDF do plano de risco, respeitando o escopo do usuário."""
    try:
        from weasyprint import HTML
    except (ImportError, OSError) as exc:
        return HttpResponse(
            'WeasyPrint não está configurado corretamente neste ambiente. '
            f'Detalhe: {exc}',
            status=500,
            content_type='text/plain; charset=utf-8',
        )

    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)
    # Verificar se o usuário tem acesso a este plano
    if not qs_planos(request.user).filter(pk=plano.pk).exists():
        return HttpResponse(status=403)
    logo_url = (settings.BASE_DIR / 'riscos' / 'assets' / 'ufsm-logo.png').as_uri()
    html_string = render_to_string('riscos/pdf_plano.html', {
        'plano': plano,
        'logo_url': logo_url,
    })
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="plano_risco_{pk}.pdf"'
    return response


@login_required
def lista_notificacoes(request):
    """Exibe as notificações do usuário e marca pendentes como lidas."""
    notificacoes = (
        Notificacao.objects
        .filter(usuario=request.user)
        .select_related('plano', 'plano__setor')
        .order_by('-criado_em')
    )
    notificacoes.filter(lida=False).update(lida=True)
    return render(request, 'riscos/lista_notificacoes.html', {
        'notificacoes': notificacoes,
    })


@login_required
def editar_plano(request, pk):
    """
    Edita um plano de risco existente.
    Requer que o usuário passe pelo pode_editar() do serviço.
    Após salvar, recalcula o status do plano com base no tratamento.
    """
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)

    if not pode_editar(plano, request.user):
        return HttpResponseForbidden('Você não tem permissão para editar este plano.')

    identificacao = getattr(plano, 'identificacao', None)
    avaliacao = getattr(plano, 'avaliacao', None)
    tratamento = getattr(plano, 'tratamento', None)
    setor_qs = _setor_qs_para_usuario(request.user)

    if request.method == 'POST':
        form_id = IdentificacaoForm(request.POST, instance=identificacao, setor_qs=setor_qs)
        form_av = AvaliacaoForm(request.POST, instance=avaliacao)
        form_tr = TratamentoForm(request.POST, instance=tratamento)

        if form_id.is_valid() and form_av.is_valid() and form_tr.is_valid():
            with transaction.atomic():
                # Atualiza o setor no PlanoDeRisco (campo extra do form de identificação)
                plano.setor = form_id.cleaned_data['setor']

                # Salva IdentificacaoRisco
                identificacao_salva = form_id.save(commit=False)
                identificacao_salva.plano = plano
                identificacao_salva.save()

                # Salva AvaliacaoRisco — save() recalcula os campos derivados
                avaliacao_salva = form_av.save(commit=False)
                avaliacao_salva.plano = plano
                avaliacao_salva.save()

                # Salva ou remove TratamentoRisco conforme preenchimento
                if form_tr.tem_dados():
                    tratamento_salvo = form_tr.save(commit=False)
                    tratamento_salvo.plano = plano
                    tratamento_salvo.save()
                    plano.status = 'com_tratamento'
                else:
                    # Seção de tratamento foi esvaziada: remove e reverte status
                    if tratamento is not None:
                        tratamento.delete()
                    plano.status = 'sem_tratamento'

                plano.save()

            messages.success(request, 'Plano de risco atualizado com sucesso.')
            return redirect('riscos:visualizar_plano', pk=plano.pk)

    else:
        # GET: pré-popula os formulários com os dados existentes.
        # O campo extra `setor` é injetado via initial.
        form_id = IdentificacaoForm(
            instance=identificacao,
            setor_qs=setor_qs,
            initial={'setor': plano.setor},
        )
        form_av = AvaliacaoForm(instance=avaliacao)
        form_tr = TratamentoForm(instance=tratamento)

    return render(request, 'riscos/editar_plano.html', {
        'plano': plano,
        'form_identificacao': form_id,
        'form_avaliacao': form_av,
        'form_tratamento': form_tr,
    })


@login_required
def excluir_plano(request, pk):
    """
    Realiza soft delete do plano de risco.
    Permitido para: Admin (qualquer plano), Gestor da Unidade (sua unidade),
    Gestor de Setor (apenas planos do seu setor).
    """
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)

    if not pode_editar(plano, request.user):
        return HttpResponseForbidden('Você não tem permissão para excluir este plano.')

    if request.method == 'POST':
        plano.soft_delete()
        messages.success(request, 'Plano de risco excluído com sucesso.')
        return redirect('riscos:lista_planos')

    return render(request, 'riscos/confirmar_exclusao.html', {'objeto': plano})


@login_required
def remanejar_plano(request, pk):
    """
    Transfere um plano de risco para outro setor dentro da mesma unidade.
    Acesso exclusivo para Gestor da Unidade e Administrador.
    O Gestor da Unidade só pode remanejar planos dentro do seu próprio escopo.
    """
    u = request.user
    perfil = getattr(u, 'perfil', '')

    if perfil not in (PERFIL_ADMINISTRADOR, PERFIL_GESTOR_UNIDADE) and not u.is_superuser:
        return HttpResponseForbidden('Apenas Gestores da Unidade ou \
                                     Administradores podem remanejar planos.')

    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)

    # Gestor da Unidade só pode remanejar planos dentro do seu escopo
    if perfil == PERFIL_GESTOR_UNIDADE:
        if not qs_planos(u).filter(pk=plano.pk).exists():
            return HttpResponseForbidden('Este plano não pertence à sua unidade.')

    unidade = plano.setor.unidade

    if request.method == 'POST':
        form = RemanejarForm(request.POST, unidade=unidade, setor_atual=plano.setor)
        if form.is_valid():
            setor_destino = form.cleaned_data['setor']
            plano.setor = setor_destino
            plano.save(update_fields=['setor'])
            messages.success(
                request,
                f'Plano remanejado para o setor "{setor_destino}" com sucesso.'
            )
            return redirect('riscos:visualizar_plano', pk=plano.pk)
    else:
        form = RemanejarForm(unidade=unidade, setor_atual=plano.setor)

    return render(request, 'riscos/remanejar_plano.html', {
        'plano': plano,
        'form': form,
        'unidade': unidade,
    })


@requer_admin
def plano_deletar(request, pk):
    """Exclusão via painel admin. Para o fluxo normal use excluir_plano."""
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)
    if request.method == 'POST':
        plano.soft_delete()
        return redirect('riscos:painel_riscos')
    return render(request, 'riscos/confirmar_exclusao.html', {'objeto': plano})
