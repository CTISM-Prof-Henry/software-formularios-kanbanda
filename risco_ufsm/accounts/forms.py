"""
Formulários do módulo de autenticação.
Sem cadastro público — apenas Admin/Gestor criam usuários.
"""

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from organizacional.models import Setor

from .models import Perfil

# pylint: disable=too-few-public-methods,no-member

# Desabilitei `too-few-public-methods` porque formulários normalmente
# não têm muitos métodos públicos além de `__init__` e `clean`.
# Desabilitei `no-member` para evitar falsos positivos ao acessar
# campos e métodos de modelos Django resolvidos dinamicamente.

Usuario = get_user_model()

class LoginForm(forms.Form):
    '''Formulário de login que aceita matrícula ou e-mail institucional.'''
    identificador = forms.CharField(
        label='Matrícula ou E-mail',
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Matrícula ou e-mail institucional',
            'autocomplete': 'username',
            'autofocus': True,
            'class': 'form-control form-control-lg',
        }),
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'senha',
            'autocomplete': 'current-password',
            'class': 'form-control form-control-lg',
        }),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

class RecuperarSenhaForm(forms.Form):
    '''
    Formulário de recuperação de senha.
    Nunca informa se o usuário existe — resposta sempre genérica.
    '''
    identificador = forms.CharField(
        label='Matrícula ou E-mail Institucional',
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Informe sua matrícula ou e-mail',
            'autocomplete': 'off',
            'class': 'form-control form-control-lg',
        }),
    )

class RedefinirSenhaForm(forms.Form):
    '''Formulário para redefinir senha via token (recuperação ou ativação).'''
    nova_senha = forms.CharField(
        label='Nova Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mínimo 8 caracteres',
            'class': 'form-control form-control-lg',
            'id': 'id_nova_senha',
        }),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repita a nova senha',
            'class': 'form-control form-control-lg',
        }),
    )

    def clean_nova_senha(self):
        '''Valida a nova senha usando as regras do Django.'''
        senha = self.cleaned_data.get('nova_senha', '')
        password_validation.validate_password(senha)
        return senha

    def clean(self):
        '''Verifica se nova_senha e confirmar_senha coincidem.'''
        cleaned = super().clean()
        s1 = cleaned.get('nova_senha')
        s2 = cleaned.get('confirmar_senha')
        if s1 and s2 and s1 != s2:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        return cleaned

class AtivacaoContaForm(RedefinirSenhaForm):
    '''Mesma estrutura de redefinição — usado na ativação inicial da conta'''
    nova_senha = forms.CharField(
        label='Criar Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Crie sua senha de acesso',
            'class': 'form-control form-control-lg',
            'id': 'id_nova_senha',
        }),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirme a senha criada',
            'class': 'form-control form-control-lg',
        }),
    )

class CadastroUsuarioForm(forms.ModelForm):
    '''
    Formulário restrito para criação de novos usuários.
    Acesso: apenas Administrador e Gestor da Unidade.
    '''
    setores = forms.ModelMultipleChoiceField(
        queryset=None,  # definido dinamicamente na view por escopo
        label='Setores / Subunidades',
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Selecione um ou mais setores para vincular o usuário.',
    )

    class Meta:
        '''
        Campos para criação de usuário, com validação de unicidade
        para matrícula e e-mail, e restrição de perfil para Gestor de Unidade.
        '''
        model = Usuario
        fields = [
            'primeiro_nome', 'sobrenome', 'matricula', 'email',
            'perfil', 'cargo', 'telefone', 'foto', 'ativo',
        ]
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Primeiro nome',
            }),
            'sobrenome': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Sobrenome',
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: 202312345',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'usuario@ufsm.br',
            }),
            'perfil': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Cargo ou função institucional',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '(99) 99999-9999', 
            }),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'primeiro_nome': 'Primeiro Nome',
            'sobrenome':     'Sobrenome',
            'matricula':     'Matrícula Institucional',
            'email':         'E-mail Institucional',
            'perfil':        'Perfil de Acesso',
            'cargo':         'Cargo / Função',
            'telefone':      'Telefone Institucional',
            'foto':          'Foto (opcional)',
            'ativo':         'Conta ativa',
        }

    def __init__(self, *args, usuario_logado=None, queryset_setores=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario_logado = usuario_logado

        # Gestor de Unidade não pode criar Administradores
        if usuario_logado and usuario_logado.perfil == Perfil.GESTOR_UNIDADE:
            self.fields['perfil'].choices = [
                (v, l) for v, l in Perfil.choices
                if v not in (Perfil.ADMIN,)
            ]

        # Setores visíveis pelo escopo do usuário logado
        if queryset_setores is not None:
            self.fields['setores'].queryset = queryset_setores

    def clean_matricula(self):
        '''
        Valida unicidade da matrícula, ignorando o próprio usuário em edição.
        '''
        mat = self.cleaned_data.get('matricula', '').strip()
        qs = Usuario.objects.filter(matricula=mat)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Esta matrícula já está cadastrada no sistema.')
        return mat

    def clean_email(self):
        '''
        Valida unicidade do e-mail, ignorando o próprio usuário em edição.
        '''
        email = self.cleaned_data.get('email', '').lower().strip()
        qs = Usuario.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este e-mail já está cadastrado no sistema.')
        return email

    def clean(self):
        '''
        Validação adicional para garantir que Gestor de
        Unidade não crie usuários com perfil Admin.
        '''
        cleaned = super().clean()
        # Gestor da Unidade não pode definir perfil Admin
        if (self.usuario_logado and
                self.usuario_logado.perfil == Perfil.GESTOR_UNIDADE and
                cleaned.get('perfil') == Perfil.ADMIN):
            self.add_error('perfil', 'Você não tem permissão para criar Administradores.')
        return cleaned

class EditarUsuarioForm(forms.ModelForm):
    '''
    Formulário para edição de usuários existentes.
    Acesso: Admin pode editar todos os campos,
    Gestor de Unidade pode editar todos exceto perfil para Admin,
    Gestor de Setor tem edição básica e restrita aos seus setores.
    '''
    setores = forms.ModelMultipleChoiceField(
        queryset=Setor.objects.none(),
        label='Setores / Subunidades',
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text='Selecione os setores ativos do usuário.',
    )

    class Meta:
        '''
        Campos para edição de usuário, com validação de unicidade para matrícula e e-mail,
        e restrição de perfil para Gestor de Unidade.
        '''
        model = Usuario
        fields = [
            'primeiro_nome', 'sobrenome', 'email',
            'perfil', 'cargo', 'telefone', 'foto', 'ativo',
        ]
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sobrenome':     forms.TextInput(attrs={'class': 'form-control'}),
            'email':         forms.EmailInput(attrs={'class': 'form-control'}),
            'perfil':        forms.Select(attrs={'class': 'form-select'}),
            'cargo':         forms.TextInput(attrs={'class': 'form-control'}),
            'telefone':      forms.TextInput(attrs={'class': 'form-control'}),
            'ativo':         forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, usuario_logado=None, queryset_setores=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario_logado = usuario_logado
        if queryset_setores is not None:
            self.fields['setores'].queryset = queryset_setores
        if self.instance.pk:
            self.fields['setores'].initial = self.instance.usuario_setores.filter(
                ativo=True,
                setor__in=self.fields['setores'].queryset,
            ).values_list('setor_id', flat=True)

        # Gestor de Setor só pode remanejar usuários entre seus setores.
        if usuario_logado and usuario_logado.perfil == Perfil.GESTOR_SETOR:
            readonly = [
                'primeiro_nome', 'sobrenome', 'email',
                'perfil', 'cargo', 'telefone', 'foto', 'ativo',
            ]
            for campo in readonly:
                self.fields[campo].disabled = True

        # Gestor de Unidade não pode alterar perfil para Admin
        if usuario_logado and usuario_logado.perfil == Perfil.GESTOR_UNIDADE:
            if self.instance.pk and self.instance.perfil == Perfil.ADMIN:
                self.fields['perfil'].disabled = True
            else:
                self.fields['perfil'].choices = [
                    (v, l) for v, l in Perfil.choices if v != Perfil.ADMIN
                ]

class MeuPerfilForm(forms.ModelForm):
    '''Todo usuário pode editar seus próprios dados básicos.'''

    class Meta:
        '''Campos para edição do próprio perfil, sem acesso a matrícula, perfil ou setores.
        '''
        model = Usuario
        fields = ['primeiro_nome', 'sobrenome', 'telefone', 'foto']
        widgets = {
            'primeiro_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sobrenome':     forms.TextInput(attrs={'class': 'form-control'}),
            'telefone':      forms.TextInput(attrs={'class': 'form-control'}),
        }

class AlterarSenhaForm(forms.Form):
    '''Formulário para alteração de senha pelo usuário logado.'''

    senha_atual = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    nova_senha = forms.CharField(
        label='Nova Senha',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'id_nova_senha',
        }),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Nova Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, usuario=None, **kwargs):
        '''Recebe o usuário logado para validação da senha atual.'''
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_senha_atual(self):
        '''Verifica se a senha atual está correta.'''
        senha = self.cleaned_data.get('senha_atual')
        if not self.usuario.check_password(senha):
            raise ValidationError('Senha atual incorreta.')
        return senha

    def clean_nova_senha(self):
        '''Valida a nova senha usando as regras do Django.'''
        senha = self.cleaned_data.get('nova_senha', '')
        password_validation.validate_password(senha, self.usuario)
        return senha

    def clean(self):
        '''Verifica se nova_senha e confirmar_senha coincidem.'''
        cleaned = super().clean()
        s1 = cleaned.get('nova_senha')
        s2 = cleaned.get('confirmar_senha')
        if s1 and s2 and s1 != s2:
            self.add_error('confirmar_senha', 'As senhas não coincidem.')
        return cleaned
