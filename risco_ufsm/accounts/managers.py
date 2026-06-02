'''
O managers do app accounts é responsável por gerenciar as
consultas aobanco de dados relacionadas aos usuários, como
criar novos usuários, buscar usuários ativos, etc.
Ele é utilizado pelo model Usuario para fornecer métodos
personalizados de consulta e criação de usuários
'''

from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    '''Gerenciador personalizado para o modelo de usuário, 
    com métodos para criar usuários e superusuários, e para filtrar usuários ativos.'''

    def get_queryset(self):
        """Retorna apenas usuários não deletados por padrão."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def todos(self):
        """Inclui usuários com soft delete (para admin e auditoria)."""
        return super().get_queryset()

    def ativos(self):
        '''Retorna apenas usuários ativos (ativo=True) e não deletados.'''
        return self.get_queryset().filter(ativo=True)

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # desabilitei o `to many arguments e positional arguments`
    # porque a criação de usuário exige muitos campos obrigatórios, e este é um caso especial.

    def create_user(self, matricula, email, *, primeiro_nome, sobrenome, password=None, **extra):
        '''Cria e salva um usuário com matrícula, email, nome e senha.'''
        if not matricula:
            raise ValueError('Matrícula é obrigatória.')
        if not email:
            raise ValueError('E-mail é obrigatório.')
        email = self.normalize_email(email)
        user  = self.model(
            matricula=matricula,
            email=email,
            primeiro_nome=primeiro_nome,
            sobrenome=sobrenome,
            **extra,
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()   # sem senha até ativação
        user.save(using=self._db)
        return user

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    # desabilitei o `to many arguments e positional arguments`
    # porque a criação de superusuário exige muitos campos obrigatórios, e este é um caso especial.

    def create_superuser(self, matricula, email, *, primeiro_nome, sobrenome, password, **extra):
        '''Cria e salva um superusuário com matrícula, email, nome e senha.'''
        extra.setdefault('perfil', 'ADMIN')
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('conta_ativada', True)
        return self.create_user(
            matricula,
            email,
            primeiro_nome=primeiro_nome,
            sobrenome=sobrenome,
            password=password,
            **extra,
        )
