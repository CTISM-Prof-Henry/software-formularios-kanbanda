"""
Cria o primeiro usuário Administrador do sistema de forma interativa.
Usado na configuração inicial do ambiente.
"""
# pylint: disable=no-member
import getpass

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

Usuario = get_user_model()


class Command(BaseCommand):
    """Comando `criar_admin_inicial`: cria um superusuário administrador inicial."""
    help = "Cria o primeiro usuário Administrador do sistema"

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('\n=== RiskShield - UFSM ==='))
        self.stdout.write(self.style.HTTP_INFO('Criação do Administrador Inicial\n'))

        if Usuario.objects.filter(perfil='ADMIN').exists():
            self.stdout.write(self.style.WARNING('Já existe um Administrador cadastrado.'))
            msg = 'Use o Django Admin para criar novos administradores.'
            self.stdout.write(self.style.WARNING(msg))
            return

        self.stdout.write('Preencha os dados do primeiro Administrador:\n')

        primeiro_nome = input('Primeiro nome: ').strip()
        sobrenome = input('Sobrenome: ').strip()
        matricula = input('Matrícula: ').strip()
        email = input('E-mail institucional: ').strip()

        while True:
            senha = getpass.getpass('Senha (mín. 8 caracteres): ')
            senha2 = getpass.getpass('Confirme a senha: ')
            if senha != senha2:
                self.stdout.write(self.style.ERROR('❌ Senhas não coincidem. Tente novamente.'))
                continue
            try:
                validate_password(senha)
                break
            except ValidationError as e:
                mensagens = ' | '.join(e.messages)
                self.stdout.write(self.style.ERROR(f'❌ {mensagens}'))

        try:
            with transaction.atomic():
                admin = Usuario.objects.create_superuser(
                    matricula=matricula,
                    email=email,
                    primeiro_nome=primeiro_nome,
                    sobrenome=sobrenome,
                    password=senha,
                )
                self.stdout.write(self.style.SUCCESS('\n✅ Administrador criado com sucesso!\n'))
                self.stdout.write(self.style.SUCCESS(f'   Nome:      {admin.get_nome_completo()}'))
                self.stdout.write(self.style.SUCCESS(f'   Matrícula: {admin.matricula}'))
                self.stdout.write(self.style.SUCCESS(f'   E-mail:    {admin.email}'))
                self.stdout.write(self.style.SUCCESS('\nAcesse: http://localhost:8000/login/\n'))
        except IntegrityError as err:
            self.stdout.write(self.style.ERROR('❌ Erro de integridade ao criar administrador:'))
            self.stdout.write(self.style.ERROR(str(err)))
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.stdout.write(self.style.ERROR('❌ Erro ao criar administrador:'))
            self.stdout.write(self.style.ERROR(str(err)))
