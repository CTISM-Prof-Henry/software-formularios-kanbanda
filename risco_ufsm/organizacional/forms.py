"""Formulários do app organizacional: unidades, setores e vínculos usuário-setor."""
from django import forms
from .models import Unidade, Setor, UsuarioSetor


class UnidadeForm(forms.ModelForm):
    """Formulário de criação e edição de unidades organizacionais."""
    class Meta:
        model  = Unidade
        fields = ['nome', 'sigla', 'tipo', 'ativo']
        widgets = {
            'nome':  forms.TextInput(attrs={'class': 'form-control',
            'placeholder': 'Nome completo da unidade'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control',
            'placeholder': 'Ex: CT, PROGRAD'}),
            'tipo':  forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome':  'Nome da Unidade',
            'sigla': 'Sigla',
            'tipo':  'Tipo',
            'ativo': 'Unidade ativa',
        }


class SetorForm(forms.ModelForm):
    """Formulário de criação e edição de setores, filtrado por permissão do usuário."""
    class Meta:
        model  = Setor
        fields = ['unidade', 'nome', 'sigla', 'ativo']
        widgets = {
            'unidade': forms.Select(attrs={'class': 'form-select'}),
            'nome':    forms.TextInput(attrs={'class': 'form-control',
            'placeholder': 'Nome do setor ou subunidade'}),
            'sigla':   forms.TextInput(attrs={'class': 'form-control',
            'placeholder': 'Ex: DAINF, GAB'}),
            'ativo':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'unidade': 'Unidade Pai',
            'nome':    'Nome do Setor',
            'sigla':   'Sigla',
            'ativo':   'Setor ativo',
        }

    def __init__(self, *args, usuario_logado=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Gestor da Unidade só vê suas unidades
        if usuario_logado and not usuario_logado.is_admin:
            unid_ids = usuario_logado.usuario_setores.filter(ativo=True).values_list(
                'setor__unidade_id', flat=True
            )
            self.fields['unidade'].queryset = Unidade.objects.filter(
                id__in=unid_ids, ativo=True
            )
        else:
            self.fields['unidade'].queryset = Unidade.objects.filter(ativo=True)


class VincularUsuarioSetorForm(forms.ModelForm):
    """Formulário para vincular um usuário a um setor com período de vigência."""
    class Meta:
        model  = UsuarioSetor
        fields = ['usuario', 'setor', 'data_inicio', 'data_fim']
        widgets = {
            'usuario':     forms.Select(attrs={'class': 'form-select'}),
            'setor':       forms.Select(attrs={'class': 'form-select'}),
            'data_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_fim':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'usuario':     'Usuário',
            'setor':       'Setor',
            'data_inicio': 'Data de Início',
            'data_fim':    'Data de Fim (opcional)',
        }
