from django.contrib.auth.models import BaseUserManager


class UsuarioManager(BaseUserManager):

    def get_queryset(self):
        """Retorna apenas usuários não deletados por padrão."""
        return super().get_queryset().filter(deleted_at__isnull=True)

    def todos(self):
        """Inclui usuários com soft delete (para admin e auditoria)."""
        return super().get_queryset()

    def ativos(self):
        return self.get_queryset().filter(ativo=True)

    def create_user(self, matricula, email, primeiro_nome, sobrenome, password=None, **extra):
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

    def create_superuser(self, matricula, email, primeiro_nome, sobrenome, password, **extra):
        extra.setdefault('perfil', 'ADMIN')
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        extra.setdefault('conta_ativada', True)
        return self.create_user(
            matricula, email, primeiro_nome, sobrenome, password, **extra
        )
