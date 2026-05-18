"""
python manage.py criar_admin_inicial

Cria o primeiro usuário Administrador do sistema de forma interativa.
Usado na configuração inicial do ambiente.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Cria o primeiro usuário Administrador do sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('\n=== RiskShield - UFSM — Criação do Administrador Inicial ===\n'))

        if Usuario.objects.filter(perfil='ADMIN').exists():
            self.stdout.write(self.style.WARNING(
                'Já existe um Administrador cadastrado. '
                'Use o Django Admin para criar novos administradores.'
            ))
            return

        self.stdout.write('Preencha os dados do primeiro Administrador:\n')

        primeiro_nome = input('Primeiro nome: ').strip()
        sobrenome     = input('Sobrenome: ').strip()
        matricula     = input('Matrícula: ').strip()
        email         = input('E-mail institucional: ').strip()

        import getpass
        while True:
            senha  = getpass.getpass('Senha (min 8 chars, maiúscula, minúscula, número, especial): ')
            senha2 = getpass.getpass('Confirme a senha: ')
            if senha != senha2:
                self.stdout.write(self.style.ERROR('  ❌ Senhas não coincidem. Tente novamente.'))
                continue
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError
            try:
                validate_password(senha)
                break
            except ValidationError as e:
                self.stdout.write(self.style.ERROR(f'  ❌ {" | ".join(e.messages)}'))

        try:
            with transaction.atomic():
                admin = Usuario.objects.create_superuser(
                    matricula=matricula,
                    email=email,
                    primeiro_nome=primeiro_nome,
                    sobrenome=sobrenome,
                    password=senha,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'\n✅ Administrador criado com sucesso!\n'
                    f'   Nome:      {admin.get_nome_completo()}\n'
                    f'   Matrícula: {admin.matricula}\n'
                    f'   E-mail:    {admin.email}\n'
                    f'\nAcesse: http://localhost:8000/login/\n'
                ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar administrador: {e}'))
