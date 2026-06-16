Documento de Divisão de Tarefas

---

## 1. Estado atual do projeto

O projeto já tem três apps funcionando e não devem ser alterados.

O app `accounts` está completo. Ele tem o modelo de usuário com matrícula como identificador principal, os quatro perfis de acesso (Administrador, Gestor da Unidade, Gestor de Setor, Servidor), ativação de conta por e-mail com token, recuperação de senha, proteção contra brute force, expiração de sessão por inatividade, CRUD completo de usuários com controle de acesso por perfil e logs de autenticação imutáveis.

O app `organizacional` está completo. Ele tem os modelos Unidade, Setor e UsuarioSetor com soft delete e histórico de alterações, além de CRUD com UI funcionando para o Administrador e Gestor da Unidade gerenciarem a estrutura da universidade.

O app `auditoria` tem apenas o modelo `LogAlteracao` criado. Não tem views nem URLs por enquanto. Será integrado na Parte 5.

O que falta é o núcleo do negócio: o módulo de riscos, o dashboard, os relatórios, as notificações e a auditoria integrada.

---

## 2. Regras que todos devem seguir

Antes de qualquer coisa: todos precisam clonar o repositório, instalar os requirements com `pip install -r requirements.txt` e rodar `python manage.py migrate` para ter o banco atualizado.

Ninguém cria migration sem ter criado o model completo. Migrations pela metade quebram o banco dos outros.

Quando criar um novo app Django (`python manage.py startapp nome`), você deve adicioná-lo em `INSTALLED_APPS` no arquivo `risco_ufsm/settings.py` e incluir suas URLs no arquivo `risco_ufsm/urls.py`.

Todos os novos models devem ter soft delete (campo `deleted_at` do tipo `DateTimeField`, nulo por padrão) em vez de exclusão física. Isso já é o padrão do projeto.

Nenhum dado jamais é apagado com `.delete()`. Sempre use soft delete ou encerramento de vínculo, como já fazem os models existentes.

Todos os templates herdam de `templates/base_sistema.html` usando `{% extends 'base_sistema.html' %}`. Não criar HTML do zero. Seguir o padrão visual já existente com Bootstrap 5.

Quando precisar restringir uma view por perfil, usar os decoradores que já existem em `accounts/decorators.py`: `@requer_admin`, `@requer_pode_criar_usuario`, `@requer_pode_gerenciar_usuarios`, ou `@requer_perfil(Perfil.GESTOR_SETOR)` para casos específicos. O `@login_required` já está embutido nesses decoradores.

---

## 3. Ordem de execução e dependências

A Parte 1 deve ser iniciada primeiro porque os outros dependem dos models que ela cria. Enquanto a Parte 1 está sendo feita, as outras pessoas podem estudar o código existente, preparar os templates base e planejar seu trabalho.

A Parte 2 começa logo após a Parte 1 ter os models e migrations prontos.

As Partes 3 e 4 podem ser iniciadas em paralelo com a Parte 2 depois que os models existirem, pois os dados de risco podem ser criados diretamente pelo admin do Django para teste.

A Parte 5 começa por último, depois que tudo mais está funcionando.

---

## 4. Atribuições

---

### Parte 1 — App configuracao e Models do app riscos

Responsável: Eduarda.

Esta parte cria toda a estrutura de dados do sistema. Nenhuma outra parte começa antes desta terminar as migrations.

**O que criar**

Criar o app de configuração com o comando `python manage.py startapp configuracao`. Adicionar `configuracao.apps.ConfiguracaoConfig` em `INSTALLED_APPS` e incluir as URLs em `risco_ufsm/urls.py` com `path('configuracao/', include('configuracao.urls'))`.

Dentro do app `configuracao`, criar três models em `configuracao/models.py`:

O model `DesafioPDI` tem os campos: `numero` (IntegerField), `descricao` (CharField de 300 caracteres), `ativo` (BooleanField default True), `criado_em` (DateTimeField auto_now_add).

O model `ObjetivoPDI` tem: `desafio` (ForeignKey para DesafioPDI, related_name='objetivos'), `codigo` (CharField de 20 caracteres, por exemplo "1.1", "1.2"), `descricao` (CharField de 300 caracteres), `ativo` (BooleanField default True).

O model `Macroprocesso` tem: `nome` (CharField de 200 caracteres), `desafio` (ForeignKey para DesafioPDI, null=True, blank=True), `ativo` (BooleanField default True).

Criar um arquivo `configuracao/admin.py` registrando os três models com `admin.site.register`. Isso permite que o Administrador cadastre esses dados pela interface admin do Django.

Criar um arquivo `configuracao/views.py`, `configuracao/forms.py` e `configuracao/urls.py` com CRUD básico para os três models. O CRUD de configuração é restrito ao Administrador com `@requer_admin`. Os templates ficam em `templates/configuracao/`.

Agora criar o app de riscos com `python manage.py startapp riscos`. Adicionar em `INSTALLED_APPS` e em `risco_ufsm/urls.py` com `path('riscos/', include('riscos.urls'))`.

Dentro de `riscos/models.py` criar os seguintes models:

```python
from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords
from organizacional.models import Setor
from configuracao.models import Macroprocesso, ObjetivoPDI

class PlanoDeRisco(models.Model):
    STATUS_SEM_TRATAMENTO = 'sem_tratamento'
    STATUS_COM_TRATAMENTO = 'com_tratamento'
    STATUS_CHOICES = [
        (STATUS_SEM_TRATAMENTO, 'Sem Tratamento'),
        (STATUS_COM_TRATAMENTO, 'Com Tratamento'),
    ]

    setor           = models.ForeignKey(Setor, on_delete=models.PROTECT, related_name='planos')
    criado_por      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                        related_name='planos_criados')
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
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    @property
    def ativo(self):
        return self.deleted_at is None
```

O model `IdentificacaoRisco` é o seguinte:

```python
class IdentificacaoRisco(models.Model):
    TIPOLOGIA_CHOICES = [
        ('ESTRATEGICO',   'Estratégico'),
        ('OPERACIONAL',   'Operacional'),
        ('INTEGRIDADE',   'Integridade'),
        ('IMAGEM',        'Imagem'),
        ('LEGAL',         'Legal / Conformidade'),
        ('FINANCEIRO',    'Financeiro / Orçamentário'),
        ('AMB_EXTERNO',   'Ambiente Externo'),
    ]

    plano           = models.OneToOneField(PlanoDeRisco, on_delete=models.CASCADE,
                                           related_name='identificacao')
    tipologia       = models.CharField(max_length=20, choices=TIPOLOGIA_CHOICES)
    macroprocesso   = models.ForeignKey(Macroprocesso, on_delete=models.SET_NULL,
                                        null=True, blank=True)
    objetivo_pdi    = models.ForeignKey(ObjetivoPDI, on_delete=models.SET_NULL,
                                        null=True, blank=True)
    descricao_evento = models.TextField('Descrição do Evento de Risco')
    causas          = models.TextField('Causas')
    consequencias   = models.TextField('Consequências')

    class Meta:
        verbose_name = 'Identificação do Risco'
```

O model `AvaliacaoRisco` é o seguinte:

```python
class AvaliacaoRisco(models.Model):
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

    plano               = models.OneToOneField(PlanoDeRisco, on_delete=models.CASCADE,
                                               related_name='avaliacao')
    probabilidade       = models.PositiveSmallIntegerField(choices=PROBABILIDADE_CHOICES)
    impacto             = models.PositiveSmallIntegerField(choices=IMPACTO_CHOICES)
    risco_inerente      = models.PositiveSmallIntegerField(editable=False, default=0)
    nivel_inerente      = models.CharField(max_length=10, choices=NIVEL_CHOICES,
                                           editable=False, blank=True)
    eficacia_controles  = models.CharField(max_length=15, choices=EFICACIA_CHOICES)
    descricao_controles = models.TextField('Descrição dos Controles Internos', blank=True)
    risco_residual      = models.FloatField(editable=False, default=0)
    nivel_residual      = models.CharField(max_length=10, choices=NIVEL_CHOICES,
                                           editable=False, blank=True)

    class Meta:
        verbose_name = 'Avaliação do Risco'

    @staticmethod
    def calcular_nivel(valor):
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
        self.risco_residual = round(self.risco_inerente * fator, 2)
        self.nivel_residual = self.calcular_nivel(self.risco_residual)
        super().save(*args, **kwargs)
```

O model `TratamentoRisco` é o seguinte:

```python
class TratamentoRisco(models.Model):
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

    plano                   = models.OneToOneField(PlanoDeRisco, on_delete=models.CASCADE,
                                                   related_name='tratamento')
    resposta                = models.CharField(max_length=15, choices=RESPOSTA_CHOICES)
    tipo_acao               = models.CharField(max_length=15, choices=TIPO_ACAO_CHOICES)
    descricao_acao          = models.TextField('Descrição da Ação')
    situacao                = models.CharField(max_length=15, choices=SITUACAO_CHOICES,
                                               default='NAO_INICIADO')
    data_inicio             = models.DateField(null=True, blank=True)
    data_conclusao_prevista = models.DateField(null=True, blank=True)
    responsavel             = models.CharField(max_length=200)
    parceiros               = models.TextField(blank=True)
    observacoes             = models.TextField(blank=True)
    resultados_observados   = models.TextField(blank=True)
    analise_critica         = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tratamento do Risco'
```

Depois de criar todos os models, rodar `python manage.py makemigrations configuracao riscos` e depois `python manage.py migrate`. Confirmar que o admin do Django mostra todos os models registrados.

Criar o arquivo `riscos/apps.py` com a classe `RiscosConfig` e adicionar `riscos.apps.RiscosConfig` em `INSTALLED_APPS`.

Criar `riscos/admin.py` registrando todos os models de riscos.

Criar um arquivo `riscos/urls.py` vazio por enquanto com `urlpatterns = []`. Isso permite que o `risco_ufsm/urls.py` inclua o app sem erros antes das views existirem.

Ao final desta parte: o banco de dados tem todas as tabelas criadas, o admin do Django permite criar macroprocessos, objetivos PDI e planos de risco manualmente para testes.

---

### Parte 2 — CRUD completo de riscos com controle de acesso por escopo

Responsável: Ana.

Esta parte do projeto cria o fluxo principal do sistema: listar, criar, visualizar, editar e excluir planos de risco, com controle rigoroso de quem pode fazer o quê.

**A função de escopo**

Criar o arquivo `riscos/services.py`. Este arquivo contém todas as funções de negócio que as views usam. A primeira e mais importante é a função que retorna o queryset correto de planos de risco para cada perfil de usuário:

```python
from .models import PlanoDeRisco

def qs_planos(usuario):
    """Retorna os planos de risco que o usuário tem permissão de ver."""
    base = PlanoDeRisco.objects.filter(deleted_at__isnull=True).select_related(
        'setor__unidade', 'criado_por', 'identificacao', 'avaliacao', 'tratamento'
    )
    if usuario.is_admin:
        return base
    if usuario.is_gestor_unidade:
        unidade_ids = usuario.get_unidades_ativas().values_list('id', flat=True)
        return base.filter(setor__unidade_id__in=unidade_ids)
    # Gestor de Setor e Servidor: apenas o próprio setor
    setor_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
    return base.filter(setor_id__in=setor_ids)
```

Adicionar também ao model `PlanoDeRisco` em `riscos/models.py` o método de verificação de permissão de edição. Isso deve ser combinado com a Pessoa da Parte 1 durante a integração:

```python
def pode_editar(self, usuario):
    if usuario.is_admin:
        return True
    if usuario.is_gestor_unidade:
        unidade_ids = usuario.get_unidades_ativas().values_list('id', flat=True)
        return self.setor.unidade_id in list(unidade_ids)
    if usuario.is_gestor_setor:
        setor_ids = usuario.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        return self.setor_id in list(setor_ids)
    return False
```

**O formulário**

Criar `riscos/forms.py` com três forms separados, um por seção. Usar `ModelForm`.
 d
O `IdentificacaoForm` herda de `ModelForm` para `IdentificacaoRisco` com os campos: `tipologia`, `macroprocesso`, `objetivo_pdi`, `descricao_evento`, `causas`, `consequencias`.

O `AvaliacaoForm` herda de `ModelForm` para `AvaliacaoRisco` com os campos: `probabilidade`, `impacto`, `eficacia_controles`, `descricao_controles`. Os campos `risco_inerente`, `nivel_inerente`, `risco_residual` e `nivel_residual` são calculados automaticamente no `save()` do model e não aparecem no form, mas são exibidos como leitura no template via JavaScript para feedback imediato ao usuário.

O `TratamentoForm` herda de `ModelForm` para `TratamentoRisco` com todos os campos do model.

**As views**

Criar `riscos/views.py` com as seguintes views.

A view `lista_planos` usa o `@login_required`, busca `qs_planos(request.user)` e aplica os filtros enviados via GET: tipologia, nivel_residual, setor, status, texto livre. O texto livre filtra em `identificacao__descricao_evento__icontains`. Calcular os contadores totais e sem tratamento. Renderizar o template `riscos/lista_planos.html`.

A view `novo_plano` exige `@login_required` e verifica que o usuário não é Servidor. Instancia os três forms. No POST, validar os três em conjunto. Dentro de um `transaction.atomic()`: criar o `PlanoDeRisco`, depois criar `IdentificacaoRisco`, `AvaliacaoRisco` (o save() calcula automaticamente), e se `TratamentoForm` tiver dados preenchidos, criar `TratamentoRisco` e atualizar `plano.status = 'com_tratamento'`. Redirecionar para a view de visualização.

A view `visualizar_plano` recebe o `pk` do plano. Buscar o plano com `get_object_or_404`. Verificar se o plano está no `qs_planos(request.user)`, senão retornar 403. Renderizar `riscos/visualizar_plano.html` em modo leitura.

A view `editar_plano` recebe o `pk`. Verificar se `plano.pode_editar(request.user)`, senão 403. No GET instanciar os três forms com os dados existentes. No POST validar e salvar dentro de `transaction.atomic()`. Após salvar, recalcular o status do plano: se o tratamento tem `descricao_acao` preenchida, o status é `com_tratamento`, senão `sem_tratamento`. Salvar o plano e redirecionar para visualização.

A view `excluir_plano` recebe o `pk`. Verificar se `plano.pode_editar(request.user)`. Fazer `plano.soft_delete()`. Adicionar mensagem de sucesso e redirecionar para `lista_planos`.

A view `remanejar_plano` é exclusiva para Gestor da Unidade e Admin. Recebe o `pk` do plano. Exibe um form com um select de setores disponíveis dentro da mesma unidade. Ao confirmar, troca o campo `setor` do plano e salva.

**As URLs**

Criar `riscos/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.lista_planos,     name='lista_planos'),
    path('novo/',                     views.novo_plano,       name='novo_plano'),
    path('<int:pk>/',                 views.visualizar_plano, name='visualizar_plano'),
    path('<int:pk>/editar/',          views.editar_plano,     name='editar_plano'),
    path('<int:pk>/excluir/',         views.excluir_plano,    name='excluir_plano'),
    path('<int:pk>/remanejar/',       views.remanejar_plano,  name='remanejar_plano'),
]
```

# parte 2.5

**Os templates**

Criar os seguintes templates em `templates/riscos/`:

`lista_planos.html`: tabela com colunas setor, tipologia, nível de risco residual (badge colorido), status (badge), data de criação, criado por, ações (ver, editar, excluir). Acima da tabela: campos de filtro em linha (selects e campo de texto) e contadores. Botão "Novo Plano" visível apenas para quem não é Servidor.

`novo_plano.html e editra_plano.html`: Três seções com cabeçalhos visuais distintos: Identificação e Análise, Avaliação, Tratamento. Na seção de avaliação, exibir abaixo dos selects de probabilidade e impacto uma linha calculada via JavaScript mostrando o risco inerente e o nível em tempo real. Ao alterar eficácia dos controles, mostrar também o risco residual calculado. Isso é JavaScript puro, sem chamada ao servidor:

```javascript
function calcularRisco() {
    const prob   = parseInt(document.getElementById('id_probabilidade').value) || 0;
    const impact = parseInt(document.getElementById('id_impacto').value) || 0;
    const inerente = prob * impact;
    document.getElementById('risco-inerente-display').textContent = inerente;

    const fatores = {
        'INEXISTENTE': 1.0, 'FRACO': 0.8, 'MEDIANO': 0.6,
        'SATISFATORIO': 0.4, 'FORTE': 0.2
    };
    const eficacia = document.getElementById('id_eficacia_controles').value;
    const residual = (inerente * (fatores[eficacia] || 1.0)).toFixed(2);
    document.getElementById('risco-residual-display').textContent = residual;
}
document.getElementById('id_probabilidade').addEventListener('change', calcularRisco);
document.getElementById('id_impacto').addEventListener('change', calcularRisco);
document.getElementById('id_eficacia_controles').addEventListener('change', calcularRisco);
```

As cores dos níveis de risco seguem o padrão: Baixo = verde (`#2ecc71`), Moderado = amarelo (`#f39c12`), Alto = laranja (`#e67e22`), Extremo = vermelho (`#e74c3c`).

`visualizar_plano.html`: exibição em leitura de todas as seções. Badges coloridos para nível inerente e residual. Botões no topo: "Editar Plano" (visível se `plano.pode_editar(request.user)`), "Gerar PDF" (link para a view de PDF da Parte 4), "Voltar à listagem".

**Menu lateral**

No arquivo `templates/base_sistema.html`, adicionar uma seção "Riscos" no menu lateral com links para lista de planos e novo plano. O link de novo plano deve ficar oculto para Servidores usando `{% if not request.user.is_servidor %}`.

--- 

### Parte 3 — Dashboard

Responsável: a ser definido pela equipe.

Esta parte cria a tela de indicadores e gráficos visível ao acessar `/dashboard/`.

**O app**

Não criar um app novo. A view de dashboard vai em `riscos/views.py` para aproveitar o `qs_planos` já definido. Adicionar a URL em `riscos/urls.py`.

**A view**

A view `dashboard` usa `@login_required` e monta um dicionário de contexto com os seguintes dados:

Contadores gerais, usando o queryset já filtrado por escopo:

```python
from django.db.models import Count, Q

planos = qs_planos(request.user)
total          = planos.count()
sem_tratamento = planos.filter(status='sem_tratamento').count()
com_tratamento = planos.filter(status='com_tratamento').count()
```

Distribuição por nível de risco residual (para os badges de resumo):

```python
from riscos.models import AvaliacaoRisco
avaliacoes = AvaliacaoRisco.objects.filter(plano__in=planos)
por_nivel = {
    'BAIXO':    avaliacoes.filter(nivel_residual='BAIXO').count(),
    'MODERADO': avaliacoes.filter(nivel_residual='MODERADO').count(),
    'ALTO':     avaliacoes.filter(nivel_residual='ALTO').count(),
    'EXTREMO':  avaliacoes.filter(nivel_residual='EXTREMO').count(),
}
```

Dados para o gráfico de distribuição por tipologia (para Chart.js), como JSON:

```python
import json
from django.core.serializers.json import DjangoJSONEncoder

por_tipologia = (
    planos.values('identificacao__tipologia')
          .annotate(total=Count('id'))
          .order_by('-total')
)
labels_tipologia = [item['identificacao__tipologia'] or 'Sem tipologia' for item in por_tipologia]
dados_tipologia  = [item['total'] for item in por_tipologia]

context['labels_tipologia'] = json.dumps(labels_tipologia, cls=DjangoJSONEncoder)
context['dados_tipologia']  = json.dumps(dados_tipologia,  cls=DjangoJSONEncoder)
```

Dados para o gráfico de riscos por setor:

```python
por_setor = (
    planos.values('setor__nome')
          .annotate(total=Count('id'))
          .order_by('-total')[:10]
)
labels_setor = [item['setor__nome'] for item in por_setor]
dados_setor  = [item['total'] for item in por_setor]

context['labels_setor'] = json.dumps(labels_setor, cls=DjangoJSONEncoder)
context['dados_setor']  = json.dumps(dados_setor,  cls=DjangoJSONEncoder)
```

Dados para a matriz probabilidade x impacto. Montar um dicionário onde a chave é `(probabilidade, impacto)` e o valor é a contagem:

```python
matriz_dados = {}
contagens = (
    avaliacoes.values('probabilidade', 'impacto')
              .annotate(total=Count('id'))
)
for item in contagens:
    matriz_dados[(item['probabilidade'], item['impacto'])] = item['total']

context['matriz_dados'] = matriz_dados
```

**O template**

Criar `templates/riscos/dashboard.html`.

No topo, quatro cards com os contadores: Total de Planos, Sem Tratamento, Com Tratamento, e um card extra de Risco Extremo destacado em vermelho.

Abaixo dos cards, a matriz probabilidade x impacto. Ela é uma tabela HTML 5x5 gerada com dois loops no template Django. O eixo Y é probabilidade (linhas de 5 a 1 de cima para baixo) e o eixo X é impacto (colunas de 1 a 5). Cada célula tem cor de fundo calculada pelo produto dos índices: produto menor que 4 é verde, até 11 amarelo, até 19 laranja, 20 ou mais vermelho. O número dentro da célula é o valor do dicionário `matriz_dados` para aquela combinação, ou zero se não houver riscos. A célula é um link que leva à listagem filtrada por probabilidade e impacto:

```html
{% for prob in '54321' %}
  <tr>
    <td>{{ prob }}</td>
    {% for imp in '12345' %}
      {% with count=matriz_dados|get_item:prob:imp %}
      <td class="matriz-celula nivel-{{ prob|times:imp|nivel_risco }}">
        <a href="{% url 'lista_planos' %}?probabilidade={{ prob }}&impacto={{ imp }}">
          {{ count|default:0 }}
        </a>
      </td>
      {% endwith %}
    {% endfor %}
  </tr>
{% endfor %}
```

Para que isso funcione, criar um arquivo `riscos/templatetags/riscos_extras.py` com filtros de template customizados para `get_item` (acessa o dicionário com chave composta) e `nivel_risco` (retorna a string do nível dado um valor numérico). O Django não tem esses filtros nativamente.

Na parte inferior do template, dois gráficos lado a lado com Bootstrap `col-md-6`. Para o gráfico de rosca (distribuição por tipologia) e o gráfico de barras horizontais (riscos por setor):

```html
{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const labelsTipologia = {{ labels_tipologia|safe }};
  const dadosTipologia  = {{ dados_tipologia|safe }};

  new Chart(document.getElementById('graficoTipologia'), {
    type: 'doughnut',
    data: {
      labels: labelsTipologia,
      datasets: [{
        data: dadosTipologia,
        backgroundColor: ['#3498db','#e74c3c','#f39c12','#2ecc71','#9b59b6','#1abc9c','#e67e22']
      }]
    },
    options: { plugins: { legend: { position: 'bottom' } } }
  });

  const labelsSetor = {{ labels_setor|safe }};
  const dadosSetor  = {{ dados_setor|safe }};

  new Chart(document.getElementById('graficoSetor'), {
    type: 'bar',
    data: {
      labels: labelsSetor,
      datasets: [{ label: 'Riscos', data: dadosSetor, backgroundColor: '#3498db' }]
    },
    options: {
      indexAxis: 'y',
      plugins: { legend: { display: false } }
    }
  });
</script>
{% endblock %}
```

O link para o dashboard no menu lateral em `base_sistema.html` deve aparecer para todos os perfis exceto Servidor.

Para o Gestor da Unidade, adicionar um select de unidade no topo do dashboard que filtra todos os dados pelo setor da unidade selecionada. Esse filtro é enviado via GET e aplicado no início da view antes de montar todos os dados.

---

### Parte 4 — Relatório PDF e notificações

Responsável: Pedro

**Configuração do ReportLab**

Instalar com `pip install reportlab` e adicionar `reportlab>=4.0` ao `requirements.txt`.

**Gerador do PDF**

Criar o arquivo `riscos/pdf_report.py`. Esse arquivo fica responsável por montar o PDF diretamente em Python usando ReportLab, sem depender de HTML, CSS, WeasyPrint, MSYS2 ou Pango. O relatório deve ser gerado em tamanho A4 e conter cabeçalho institucional com a marca da UFSM, título "Plano de Análise de Risco", número do plano, setor, data de emissão e as três seções principais do plano: Identificação e Análise, Avaliação e Tratamento. As informações devem ser organizadas em tabelas, e os níveis de risco devem aparecer com destaque colorido.

Estrutura principal usada no gerador:

```python
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def gerar_plano_pdf(plano):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.7 * cm,
        bottomMargin=1.7 * cm,
    )

    estilos = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph('PLANO DE ANÁLISE DE RISCO', estilos['Title']))
    elementos.append(Spacer(1, 12))

    tabela = Table([
        ['Plano', f'#{plano.pk}'],
        ['Setor', str(plano.setor)],
        ['Status', plano.get_status_display()],
    ])
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f3f6')),
    ]))
    elementos.append(tabela)

    doc.build(elementos)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
```

No projeto, esse exemplo foi expandido com funções auxiliares para evitar repetição, incluir a logo da UFSM, formatar textos longos, montar as tabelas das seções do plano e exibir os níveis de risco com cores.

**View de geração do PDF**

Adicionar em `riscos/views.py`:

```python
from django.http import HttpResponse

@login_required
def gerar_pdf(request, pk):
    plano = get_object_or_404(PlanoDeRisco, pk=pk, deleted_at__isnull=True)
    # Verificar se o usuário tem acesso a este plano
    if not qs_planos(request.user).filter(pk=plano.pk).exists():
        return HttpResponse(status=403)

    from .pdf_report import gerar_plano_pdf
    pdf = gerar_plano_pdf(plano)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="plano_risco_{pk}.pdf"'
    return response
```

Adicionar a URL `path('<int:pk>/pdf/', views.gerar_pdf, name='gerar_pdf')` em `riscos/urls.py`.

**Model de Notificação**

Adicionar em `riscos/models.py`:

```python
class Notificacao(models.Model):
    TIPO_ATRASO   = 'ATRASO'
    TIPO_CHOICES  = [(TIPO_ATRASO, 'Plano de Tratamento Atrasado')]

    usuario       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                      related_name='notificacoes')
    plano         = models.ForeignKey(PlanoDeRisco, on_delete=models.CASCADE,
                                      related_name='notificacoes')
    tipo          = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensagem      = models.TextField()
    lida          = models.BooleanField(default=False)
    criado_em     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificação'
        ordering = ['-criado_em']
```

Rodar `python manage.py makemigrations riscos` depois de adicionar este model.

**Management command para detectar atrasos**

Criar `riscos/management/__init__.py`, `riscos/management/commands/__init__.py` e `riscos/management/commands/verificar_atrasos.py`:

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from riscos.models import TratamentoRisco, Notificacao

class Command(BaseCommand):
    help = 'Marca tratamentos vencidos como Atrasado e gera notificações.'

    def handle(self, *args, **options):
        hoje = timezone.localdate()
        atrasados = TratamentoRisco.objects.filter(
            data_conclusao_prevista__lt=hoje,
            situacao__in=['NAO_INICIADO', 'EM_EXECUCAO']
        ).select_related('plano__setor', 'plano__criado_por')

        for t in atrasados:
            t.situacao = 'ATRASADO'
            t.save(update_fields=['situacao'])

            # Criar notificação para o criador do plano se ainda não existir
            Notificacao.objects.get_or_create(
                usuario=t.plano.criado_por,
                plano=t.plano,
                tipo=Notificacao.TIPO_ATRASO,
                lida=False,
                defaults={'mensagem': f'O plano #{t.plano.pk} do setor {t.plano.setor} '
                                      f'está com tratamento atrasado.'}
            )
        self.stdout.write(f'{atrasados.count()} planos marcados como atrasados.')
```

Rodar com `python manage.py verificar_atrasos`. Em produção, configurar como cron diário.

**Exibir badge de notificações no header**

Criar um context processor em `riscos/context_processors.py`:

```python
def notificacoes(request):
    if not request.user.is_authenticated:
        return {}
    from riscos.models import Notificacao
    count = Notificacao.objects.filter(usuario=request.user, lida=False).count()
    return {'notificacoes_count': count}
```

Adicionar `riscos.context_processors.notificacoes` na lista `context_processors` do `TEMPLATES` em `settings.py`.

No `base_sistema.html`, adicionar no header ao lado do botão "Meu Perfil" um badge com `{{ notificacoes_count }}` se maior que zero.

Criar a view `lista_notificacoes` que exibe as notificações do usuário e marca como lidas ao acessar. Adicionar URL `path('notificacoes/', views.lista_notificacoes, name='lista_notificacoes')` em `riscos/urls.py`.

---

### Parte 5 — Auditoria integrada, histórico visual, testes e polimento final

Responsável: João Pedro.

Esta parte é executada por último, depois que as outras quatro estão funcionando.

**Conectar a auditoria via signals**

Criar o arquivo `riscos/signals.py`. O objetivo é gravar um `LogAlteracao` sempre que um plano de risco for criado ou modificado.

```python
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
```

Para registrar o usuário que fez a alteração no `LogAlteracao`, aproveitar o `HistoryRequestMiddleware` do `django-simple-history` que já está configurado no projeto. Alternativamente, passar o usuário via `kwargs` se a view chamar o save com o contexto disponível.

Ativar os signals criando `riscos/apps.py` com:

```python
from django.apps import AppConfig

class RiscosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'riscos'

    def ready(self):
        import riscos.signals  # noqa
```

**Histórico visual no plano**

O `django-simple-history` já está instalado e os models de risco terão `history = HistoricalRecords()` adicionados pela Parte 1. A Parte 5 só precisa exibir isso na tela.

Na view `visualizar_plano` da Parte 2, adicionar ao contexto:

```python
context['historico'] = plano.history.all()[:20]
```

No template `visualizar_plano.html`, adicionar uma seção "Histórico de Alterações" no final da página com uma tabela mostrando data, usuário e tipo de alteração.

**Testes**

Criar `riscos/tests/test_calculos.py` com testes para as regras de negócio:

```python
from django.test import TestCase
from riscos.models import AvaliacaoRisco

class TesteCalculos(TestCase):
    def test_risco_inerente(self):
        # prob=3, impacto=4 -> inerente=12
        a = AvaliacaoRisco(probabilidade=3, impacto=4, eficacia_controles='MEDIANO')
        a.save()
        self.assertEqual(a.risco_inerente, 12)

    def test_nivel_alto(self):
        self.assertEqual(AvaliacaoRisco.calcular_nivel(12), 'ALTO')
        self.assertEqual(AvaliacaoRisco.calcular_nivel(19), 'ALTO')

    def test_nivel_extremo(self):
        self.assertEqual(AvaliacaoRisco.calcular_nivel(20), 'EXTREMO')

    def test_risco_residual_forte(self):
        a = AvaliacaoRisco(probabilidade=5, impacto=5, eficacia_controles='FORTE')
        a.save()
        # inerente=25, fator=0.2 -> residual=5.0
        self.assertEqual(a.risco_residual, 5.0)
        self.assertEqual(a.nivel_residual, 'MODERADO')
```

Criar `riscos/tests/test_acesso.py` com testes de scoping, verificando que um Gestor de Setor não visualiza nem edita riscos de outro setor.

Rodar os testes com `python manage.py test riscos`.

**Polimento do menu lateral**

No `base_sistema.html`, revisar o menu lateral para exibir apenas o que cada perfil pode usar:

- Servidor: vê "Riscos" (listagem do setor, apenas leitura), não vê "Novo Plano" nem os menus de configuração ou estrutura.
- Gestor de Setor: vê "Riscos" e "Novo Plano", não vê configuração nem estrutura organizacional.
- Gestor da Unidade: vê "Riscos", "Dashboard", pode ver usuários da sua unidade.
- Administrador: vê tudo incluindo "Configuração", "Estrutura", "Logs".

Adicionar o link para "Configuração" no menu visível apenas para Administrador, com subitens para Macroprocessos, Desafios PDI e Objetivos PDI.

**Verificação final**

Testar o fluxo completo: criar um usuário Gestor de Setor, vincular a um setor, criar um plano de risco, verificar que o risco inerente e residual calculam corretamente, verificar que o status muda para "Com Tratamento" ao preencher a seção de tratamento, verificar que a geração de PDF funciona, verificar que o dashboard exibe os dados corretos.

---

## 5. Resumo das responsabilidades

Parte 1 (Eduarda): app configuracao (DesafioPDI, ObjetivoPDI, Macroprocesso) + app riscos (PlanoDeRisco, IdentificacaoRisco, AvaliacaoRisco, TratamentoRisco) com migrations, admin e lógica de cálculo no save().

Parte 2 (Ana): CRUD completo de riscos com a função de escopo por perfil, formulário em três seções com cálculo visual em JavaScript, templates de listagem, criação, edição e visualização, controle de permissão de edição e exclusão.

Parte 3: dashboard com contadores, matriz probabilidade x impacto em HTML colorido, gráfico de rosca por tipologia e gráfico de barras por setor usando Chart.js, scoping por perfil.

Parte 4 (Pedro): geração de PDF com ReportLab, model Notificacao, management command de verificação de atrasos, badge de notificações no header.

Parte 5: signals conectando LogAlteracao aos modelos de risco, histórico visual na tela do plano, testes das regras de cálculo e de scoping, polimento do menu lateral por perfil.
