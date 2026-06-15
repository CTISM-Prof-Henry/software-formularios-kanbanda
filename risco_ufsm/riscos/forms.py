'''
formulários dos riscos:
- identificação
- avaliação
- tratamento
- remanejamento
'''

from django import forms
from organizacional.models import Setor
from .models import IdentificacaoRisco, AvaliacaoRisco, TratamentoRisco

class IdentificacaoForm(forms.ModelForm):
    '''Formulario para a idntificação do risco'''

    setor = forms.ModelChoiceField(
        queryset=Setor.objects.none(),
        label='Setor / Departamento responsável',
        empty_label='Selecione o setor...',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = IdentificacaoRisco
        fields = ['tipologia',
                'macroprocesso',
                'objetivo_pdi',
                'descricao_evento',
                'causas',
                'consequencias',]
        widgets = {
            'tipologia': forms.Select(attrs={'class': 'form-select'}),
            'macroprocesso': forms.Select(attrs={'class': 'form-select'}),
            'objetivo_pdi': forms.Select(attrs={'class': 'form-select'}),
            'descricao_evento': forms.Textarea(attrs={'class': 'form-control', 
                                                        'rows': 4, 'placeholder': 
                                                        'Descreva o evento de risco...'}),
            'causas': forms.Textarea(attrs={'class': 'form-control', 
                                            'rows': 3, 'placeholder': 
                                            'Quais são as causas raiz?'}),
            'consequencias': forms.Textarea(attrs={'class': 'form-control', 
                                                   'rows': 3, 'placeholder': 
                                                    'Quais os impactos caso ocorra?'}),
        }
        labels = {
            'tipologia': 'Tipologia / Categoria de risco',
            'macroprocesso': 'Macroprocesso institucional',
            'objetivo_pdi': "Objetivo do Plano de Desenvolvimento Individual",
            'descricao_evento': "Descrição do evento de risco",
            'causas': 'Causas do risco',
            'consequencias': 'Consequências / efeitos',
        }

    def __init__(self, *args, setor_qs=None, **kwargs):
        """
        setor_qs: queryset de Setor filtrado conforme o perfil do usuário.
        Se não fornecido, mantém queryset vazio (nenhum setor exibido).
        """
        super().__init__(*args, **kwargs)
        if setor_qs is not None:
            self.fields['setor'].queryset = setor_qs


class AvaliacaoForm(forms.ModelForm):
    '''
    mostra apenas os campos de entrada do user,
    os outros são calculados automaticamente e preenchidos pelo save() 
    e o calculo é feito pelo JS no template
    '''

    class Meta:
        model = AvaliacaoRisco
        fields = ['probabilidade',
                'impacto',
                'eficacia_controles',
                'descricao_controles',]
        widgets = {
            'probabilidade': forms.Select(attrs={'class': 'form-select', 
                                                'id': 'id_probabilidade'}),
            'impacto': forms.Select(attrs={'class': 'form-select', 
                                            'id': 'id_impacto'}),
            'eficacia_controles': forms.Select(attrs={'class': 'form-select',
                                                        'id': 'id_eficacia_controles'}),
            'descricao_controles': forms.Textarea(attrs={'class': 'form-control', 
                                                        'rows': 3, 'placeholder': 
                                                        'Descreva os controles internos'}),
        }
        labels = {
            'probabilidade': 'Probabilidade',
            'impacto': 'Impacto',
            'eficacio_controles': 'Eficácia dos controles internos existentes',
            'descricao_controles': 'Descrição dos controles internos aplicados',
        }


class TratamentoForm(forms.ModelForm):
    '''
    formulario onde todos o scampos são opcionais para o tratamento'''
    class Meta:
        model = TratamentoRisco
        fields = [
            'resposta',
            'tipo_acao',
            'descricao_acao',
            'situacao',
            'data_inicio',
            'data_conclusao_prevista',
            'responsavel',
            'parceiros',
            'observacoes',
            'resultados_observados',
            'analise_critica',]        
        widgets = {
            'resposta': forms.Select(attrs={'class': 'form-select'}),
            'tipo_acao': forms.Select(attrs={'class': 'form-select'}),
            'descricao_acao': forms.Textarea(attrs={'class': 'form-control', 
                                                    'rows': 4, 'placeholder': 
                                                    'Descreva a ação'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, 
                                                    format='%Y-%m-%d'),
            'data_conclusao_prevista': forms.DateInput(attrs={'type': 'date', 
                                                                'class': 'form-control'}, 
                                                                format='%Y-%m-%d'),
            'responsavel': forms.TextInput(attrs={'class': 'form-control', 
                                                    'placeholder': 'Responsável pelo tratamento'}),
            'parceiros': forms.Textarea(attrs={'class': 'form-control',
                                                'rows': 2, 'placeholder':
                                                'Outros setores ou pessoas envolvidas'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 
                                                    'rows': 3, 'placeholder': 'Observações'}),
            'resultados_observados': forms.Textarea(attrs={'class': 'form-control', 
                                                           'rows': 3, 'placeholder': 
                                                            'Descreva os resultados observados'}),
            'analise_critica': forms.Textarea(attrs={'class': 'form-control', 
                                                        'rows': 3, 'placeholder': 
                                                        'Faça uma análise do tratamento'}),
        }
        labels = {
            'resposta': 'Resposta ao risco',
            'tipo_acao': 'Tipo de ação',
            'descricao_acao': 'descrição da ação de mitigação',
            'situacao': 'Situação do tratamento',
            'data_inicio': 'data de início',
            'data_conclusao_prevista': 'Data prevista da conclusão',
            'responsavel': 'Responsávelpela execução',
            'parceiros': 'Parceiros / Intervenientes',
            'observacoes': 'Observações',
            'resultados_observados': 'Resultados observados',
            'analise_critica': 'Análise crítica da efetividade',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # toda a seção de tratamento é opcional
        for field in self.fields.values():
            field.required = False

    def tem_dados(self):
        """
        Retorna True se a seção de tratamento foi minimamente preenchida.
        Critério: campo descricao_acao não vazio.
        Usado pela view para decidir se cria/mantém o TratamentoRisco
        e para calcular o status do PlanoDeRisco.
        """
        return bool(self.cleaned_data.get('descricao_acao', '').strip())


class RemanejarForm(forms.Form):
    """
    Permite ao Gestor da Unidade ou Admin transferir um plano de risco
    para outro setor dentro da mesma unidade organizacional.
    """

    setor = forms.ModelChoiceField(
        queryset=Setor.objects.none(),
        label='Novo setor destino',
        empty_label='Selecione o setor destino...',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, unidade=None, setor_atual=None, **kwargs):
        """
        unidade: instância de Unidade — limita a seleção aos setores da mesma unidade.
        setor_atual: exclui o setor atual da lista (evita remanejar para o mesmo setor).
        """
        super().__init__(*args, **kwargs)
        if unidade is not None:
            qs = Setor.objects.filter(
                unidade=unidade,
                deleted_at__isnull=True,
            ).order_by('nome')
            if setor_atual is not None:
                qs = qs.exclude(pk=setor_atual.pk)
            self.fields['setor'].queryset = qs
