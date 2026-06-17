"""
O models define os modelos de dados relacionados a usuários, autenticação e segurança.
"""
import uuid
import logging
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.conf import settings

from simple_history.models import HistoricalRecords
from organizacional.models import Unidade

from .managers import UsuarioManager

logger = logging.getLogger('accounts')
#  Perfis do sistema

class Perfil(models.TextChoices):
    '''Define os perfis de usuário do sistema, que determinam as permissões e acessos.
    - ADMIN: Acesso total, pode gerenciar usuários, ver logs, etc.
    - GESTOR_UNIDADE: Pode criar e gerenciar usuários dentro da unidade, 
    mas não pode acessar logs ou criar outros gestores.
    - GESTOR_SETOR: Pode gerenciar usuários do mesmo setor,
    mas não pode criar gestores ou acessar logs.
    - SERVIDOR: Acesso básico, sem permissões administrativas.'''
    ADMIN          = 'ADMIN',          'Administrador do Sistema'
    GESTOR_UNIDADE = 'GESTOR_UNIDADE', 'Gestor da Unidade'
    GESTOR_SETOR   = 'GESTOR_SETOR',   'Gestor de Setor'
    SERVIDOR       = 'SERVIDOR',       'Servidor / Colaborador'


# pylint: disable=too-few-public-methods,no-member
# Desabilitei `too-few-public-methods` porque modelos Django normalmente
# não têm muitos métodos públicos além de `__str__` e helpers relacionados.
# Desabilitei `no-member` para evitar falsos positivos ao acessar
# campos e métodos de modelos Django resolvidos dinamicamente, como `objects` e `save()`.

class Usuario(AbstractBaseUser, PermissionsMixin):
    '''Modelo de usuário personalizado, usando matrícula ou 
    e-mail institucional como identificador.'''

    # Identificação
    primeiro_nome = models.CharField('Primeiro Nome', max_length=80)
    sobrenome = models.CharField('Sobrenome', max_length=100)
    matricula = models.CharField('Matrícula', max_length=20, unique=True, db_index=True)
    email = models.EmailField('E-mail Institucional', unique=True, db_index=True)
    foto = models.ImageField('Foto', upload_to='fotos/', blank=True, null=True)
    telefone = models.CharField('Telefone Institucional', max_length=20, blank=True)
    cargo = models.CharField('Cargo / Função', max_length=120, blank=True)

    # Perfil e permissões
    perfil = models.CharField(
        'Perfil',
        max_length=20,
        choices=Perfil.choices,
        default=Perfil.SERVIDOR,
        db_index=True,
    )

    # Estado da conta
    ativo = models.BooleanField('Ativo', default=True, db_index=True)
    conta_ativada = models.BooleanField('Conta Ativada', default=False)
    is_staff = models.BooleanField('Acesso Admin Django', default=False)

    # Rastreabilidade
    criado_em = models.DateTimeField('Criado em',    auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    deleted_at = models.DateTimeField('Excluído em',  null=True, blank=True, db_index=True)
    criado_por = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='usuarios_criados',
        verbose_name='Criado por',
    )
    ultimo_login_ip = models.GenericIPAddressField('IP do Último Login', null=True, blank=True)

    # Histórico de alterações
    history = HistoricalRecords(
        history_change_reason_field=models.TextField(null=True),
        excluded_fields=['last_login', 'ultimo_login_ip'],
    )

    objects = UsuarioManager()

    USERNAME_FIELD  = 'matricula'
    REQUIRED_FIELDS = ['email', 'primeiro_nome', 'sobrenome']

    class Meta:
        '''Configurações do modelo de usuário, incluindo nome legível e ordenação padrão. 
        Ele é utilizado pelo backend de autenticação para buscar usuários usando matrícula
        ou e-mail institucional, e verifica se a conta está ativa e ativada.'''
        verbose_name = 'Usuário'
        verbose_name_plural  = 'Usuários'
        ordering = ['primeiro_nome', 'sobrenome']

    def __str__(self):
        '''Retorna uma representação legível do usuário, mostrando nome completo e matrícula.'''
        return f'{self.get_nome_completo()} ({self.matricula})'

    #  Helpers básicos

    def get_nome_completo(self):
        '''Retorna o nome completo do usuário, combinando primeiro nome e sobrenome.'''
        return f'{self.primeiro_nome} {self.sobrenome}'.strip()

    def get_iniciais(self):
        '''Retorna as iniciais do usuário, usando a primeira letra do primeiro nome e sobrenome.'''
        partes = self.get_nome_completo().split()
        if len(partes) >= 2:
            return f'{partes[0][0]}{partes[-1][0]}'.upper()

        # pylint: disable=unsubscriptable-object
        # Desabilitei `unsubscriptable-object` porque `partes[0][0]` é uma forma comum
        # de obter a primeira letra, e o linter não reconhece que `partes[0]` é uma string.

        return self.matricula[:2].upper()

    def soft_delete(self, usuario_acao=None):
        """Desativa o usuário sem apagar do banco."""
        self.ativo = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['ativo', 'deleted_at', 'atualizado_em'])
        logger.info('Usuário %s desativado por %s', self.matricula, usuario_acao)

    # Verificadores de perfil

    @property
    def is_admin(self):
        '''Retorna True se o usuário tem perfil de administrador, caso contrário False.'''
        return self.perfil == Perfil.ADMIN

    @property
    def is_gestor_unidade(self):
        '''Retorna True se o usuário tem perfil de gestor de unidade, caso contrário False.'''
        return self.perfil == Perfil.GESTOR_UNIDADE

    @property
    def is_gestor_setor(self):
        '''Retorna True se o usuário tem perfil de gestor de setor, caso contrário False.'''
        return self.perfil == Perfil.GESTOR_SETOR

    @property
    def is_servidor(self):
        '''Retorna True se o usuário tem perfil de servidor, caso contrário False.'''
        return self.perfil == Perfil.SERVIDOR

    # Permissões funcionais

    @property
    def pode_criar_usuario(self):
        '''Retorna True se o usuário pode criar outros usuários, caso contrário False.'''
        return self.perfil in (Perfil.ADMIN, Perfil.GESTOR_UNIDADE)

    @property
    def pode_gerenciar_usuarios(self):
        '''Retorna True se o usuário pode gerenciar outros usuários.
        Caso contrário, retorna False.'''
        return self.perfil in (Perfil.ADMIN, Perfil.GESTOR_UNIDADE, Perfil.GESTOR_SETOR)

    @property
    def pode_alterar_perfil(self):
        '''Retorna True se o usuário pode alterar o perfil de outros usuários, se não False.'''
        return self.perfil in (Perfil.ADMIN, Perfil.GESTOR_UNIDADE)

    @property
    def pode_ver_logs(self):
        '''Retorna True se o usuário pode ver os logs do sistema, caso contrário False.'''
        return self.perfil == Perfil.ADMIN

    def pode_editar_usuario(self, alvo):
        """Verifica se self pode editar o usuário alvo."""
        if self.perfil == Perfil.ADMIN:
            return True
        if self.perfil == Perfil.GESTOR_UNIDADE:
            if alvo.perfil == Perfil.ADMIN:
                return False
            return True
        if self.perfil == Perfil.GESTOR_SETOR:
            # Apenas dados básicos do mesmo setor, sem criar/promover
            return self._mesmo_setor(alvo)
        return False

    def _mesma_unidade(self, outro):
        """Verifica se outro usuário pertence à mesma unidade."""
        minhas_unidades = set(
            self.usuario_setores.filter(ativo=True)
                .values_list('setor__unidade_id', flat=True)
        )
        outras_unidades = set(
            outro.usuario_setores.filter(ativo=True)
                 .values_list('setor__unidade_id', flat=True)
        )
        return bool(minhas_unidades & outras_unidades)

    def _mesmo_setor(self, outro):
        '''Verifica se outro usuário pertence ao mesmo setor (para gestores de setor).'''
        meus_setores = set(
            self.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        )
        outros_setores = set(
            outro.usuario_setores.filter(ativo=True).values_list('setor_id', flat=True)
        )
        return bool(meus_setores & outros_setores)

    # visual helpers/firulas

    def get_perfil_badge(self):
        '''Retorna uma tupla (classe_css, emoji) para exibir o perfil do usuário de forma visual.'''
        return {
            Perfil.ADMIN:          ('badge-admin',    '⚙️'),
            Perfil.GESTOR_UNIDADE: ('badge-gu',       '🏛️'),
            Perfil.GESTOR_SETOR:   ('badge-gs',       '🗂️'),
            Perfil.SERVIDOR:       ('badge-servidor', '👤'),
        }.get(self.perfil, ('badge-servidor', '👤'))

    def get_setores_ativos(self):
        '''Retorna os setores ativos aos quais o usuário pertence,
        para exibição e verificação de permissões.'''
        return self.usuario_setores.filter(ativo=True).select_related('setor__unidade')

    def get_unidades_ativas(self):
        '''Retorna as unidades ativas às quais o usuário pertence,'''
        ids = self.usuario_setores.filter(ativo=True).values_list(
            'setor__unidade_id', flat=True
        ).distinct()
        return Unidade.objects.filter(id__in=ids)

class TokenAtivacao(models.Model):
    """
    Token enviado por e-mail para o usuário ativar a conta e criar a senha
    """
    usuario  = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        related_name='tokens_ativacao',
    )
    token    = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    usado    = models.BooleanField(default=False)
    usado_em = models.DateTimeField(null=True, blank=True)
    ip_ativacao = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        '''Configurações do modelo de token de ativação.
        Inclui nome legível, ordenação por data de criação e regras de uso.
        Usado para enviar link de ativação por e-mail; o token expira após
        período configurável e só pode ser usado uma vez.'''

        verbose_name = 'Token de Ativação'
        verbose_name_plural = 'Tokens de Ativação'
        ordering = ['-criado_em']

    def __str__(self):
        '''Retorna a representação string do token de ativação.'''
        return f'Ativação de {self.usuario.matricula} — exp: {self.expira_em:%d/%m/%Y %H:%M}'

    def save(self, *args, **kwargs):
        '''Define a data de expiração do token ao salvar, se ainda não estiver definida.'''
        if not self.pk and not self.expira_em:
            horas = getattr(settings, 'TOKEN_ATIVACAO_HORAS', 48)
            self.expira_em = timezone.now() + timedelta(hours=horas)
        super().save(*args, **kwargs)

    def esta_valido(self):
        '''Verifica se o token ainda não foi usado e não expirou.'''
        return not self.usado and timezone.now() < self.expira_em

    def marcar_usado(self, ip=None):
        '''Marca o token como usado e registra o IP de uso.'''
        self.usado    = True
        self.usado_em = timezone.now()
        self.ip_ativacao = ip
        self.save(update_fields=['usado', 'usado_em', 'ip_ativacao'])

class TokenRecuperacaoSenha(models.Model):
    """
    Token de redefinição de senha que expira em 15 minutos.
    Obiviamente não retorna se o usuário existe ou não, para não vazar informação
    """
    usuario       = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        related_name='tokens_recuperacao',
    )
    token         = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    criado_em     = models.DateTimeField(auto_now_add=True)
    expira_em     = models.DateTimeField()
    usado         = models.BooleanField(default=False)
    usado_em      = models.DateTimeField(null=True, blank=True)
    ip_solicitante = models.GenericIPAddressField(null=True, blank=True)
    ip_uso        = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        '''Configurações do modelo de token de recuperação de senha,
        incluindo nome legível e ordenação por data de criação.
        Ele é utilizado para enviar um link de redefinição de senha por e-mail para o usuário, 
        permitindo que ele crie uma nova senha.
        O token expira após um período curto (15 minutos) e só pode ser usado uma vez. 
        Ele não revela se o usuário existe ou não para evitar vazamento de informações.'''
        verbose_name = 'Token de Recuperação de Senha'
        verbose_name_plural = 'Tokens de Recuperação de Senha'
        ordering = ['-criado_em']

    def __str__(self):
        '''Retorna a representação string do token de recuperação de senha.'''
        return f'Recuperação de {self.usuario.matricula} — exp: {self.expira_em:%d/%m/%Y %H:%M}'

    def save(self, *args, **kwargs):
        '''Define a data de expiração do token ao salvar, se ainda não estiver definida.'''
        if not self.pk and not self.expira_em:
            minutos = getattr(settings, 'TOKEN_RECUPERACAO_MINUTOS', 15)
            self.expira_em = timezone.now() + timedelta(minutes=minutos)
        super().save(*args, **kwargs)

    def esta_valido(self):
        '''Verifica se o token de recuperação de senha ainda é válido.'''
        return not self.usado and timezone.now() < self.expira_em

    def marcar_usado(self, ip=None):
        '''Marca o token como usado e registra o IP de uso.'''
        self.usado    = True
        self.usado_em = timezone.now()
        self.ip_uso   = ip
        self.save(update_fields=['usado', 'usado_em', 'ip_uso'])


# Log de acessos

class LogAcesso(models.Model):
    """
    Registro imutável de todas as tentativas de autenticação.
    Ele nunca pode ser apagado ou editado por motivos óbvios de segurança e auditoria
    - se ele pudesse ser apagado, então ele poderia simplesmente não existir né -
    """
    TIPO_LOGIN_OK    = 'LOGIN_OK'
    TIPO_LOGIN_FALHA = 'LOGIN_FALHA'
    TIPO_LOGOUT      = 'LOGOUT'
    TIPO_ATIVACAO    = 'ATIVACAO'
    TIPO_RECUPERACAO = 'RECUPERACAO_SENHA'
    TIPO_BLOQUEIO    = 'BLOQUEIO_IP'
    TIPO_SESSAO_EXP  = 'SESSAO_EXPIRADA'

    TIPO_CHOICES = [
        (TIPO_LOGIN_OK,    'Login bem-sucedido'),
        (TIPO_LOGIN_FALHA, 'Tentativa de login falha'),
        (TIPO_LOGOUT,      'Logout'),
        (TIPO_ATIVACAO,    'Ativação de conta'),
        (TIPO_RECUPERACAO, 'Recuperação de senha'),
        (TIPO_BLOQUEIO,    'IP bloqueado por brute force'),
        (TIPO_SESSAO_EXP,  'Sessão expirada'),
    ]

    tipo              = models.CharField('Tipo', max_length=30, choices=TIPO_CHOICES, db_index=True)
    usuario           = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='logs_acesso',
    )
    identificador_tentado = models.CharField(
        'Matrícula/E-mail tentado', max_length=200, blank=True,
    )
    ip                = models.GenericIPAddressField('Endereço IP', null=True, blank=True)
    user_agent        = models.TextField('User-Agent', blank=True)
    detalhes          = models.TextField('Detalhes', blank=True)
    criado_em         = models.DateTimeField('Data/Hora', auto_now_add=True, db_index=True)

    class Meta:
        '''Configurações do modelo de log de acesso, incluindo nome legível, 
        ordenação por data e proteção contra exclusão.'''
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        ordering = ['-criado_em']

    def __str__(self):
        '''Retorna uma representação legível do log de acesso, mostrando data, tipo e IP.'''
        return f'[{self.criado_em:%d/%m/%Y %H:%M}] {self.tipo} — {self.ip}'

    def delete(self, *args, **kwargs):
        '''Logs de acesso não podem ser apagados por motivos de segurança e auditoria.'''
        raise PermissionError('Logs de acesso não podem ser apagados.')


# Tentativas de login (brute force)
# rastreia tentativas falhas vindas de um mesmo IP e
# bloqueia por 15 minutos depois de 5 tentativas falhas

class TentativaLogin(models.Model):
    """Rastreia tentativas falhas por IP para proteção contra brute force."""
    ip            = models.GenericIPAddressField('IP', db_index=True)
    tentativas    = models.PositiveSmallIntegerField('Tentativas', default=0)
    bloqueado_ate = models.DateTimeField('Bloqueado até', null=True, blank=True)
    ultima_tentativa = models.DateTimeField('Última tentativa', auto_now=True)

    class Meta:
        '''Configurações do modelo de tentativa de login,
        incluindo nome legível e proteção contra exclusão.
        Ele é utilizado para rastrear tentativas de login falhas vindas de um mesmo IP
        e bloquear o acesso por um período de tempo após um
        número configurável de tentativas falhas.'''

        verbose_name = 'Tentativa de Login'
        verbose_name_plural = 'Tentativas de Login'

    def __str__(self):
        '''Retorna uma representação legível da tentativa de login,
        mostrando IP e número de tentativas.'''
        return f'{self.ip} — {self.tentativas} tentativas'

    def esta_bloqueado(self):
        '''Verifica se o IP está atualmente bloqueado devido a tentativas falhas.'''
        if self.bloqueado_ate and timezone.now() < self.bloqueado_ate:
            return True
        return False

    def incrementar(self, max_tentativas=5, bloqueio_minutos=15):
        '''Incrementa o contador de tentativas e bloqueia o IP se atingir o limite.'''
        # Se o bloqueio anterior já expirou, reinicia o contador
        if self.bloqueado_ate and timezone.now() >= self.bloqueado_ate:
            self.tentativas = 0
            self.bloqueado_ate = None

        self.tentativas += 1
        if self.tentativas >= max_tentativas:
            self.bloqueado_ate = timezone.now() + timedelta(minutes=bloqueio_minutos)
        self.save()
        return self.esta_bloqueado()

    def resetar(self):
        '''Reseta o contador de tentativas e desbloqueia o IP.'''
        self.tentativas = 0
        self.bloqueado_ate = None
        self.save()
