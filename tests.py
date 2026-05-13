import pytest

from accounts.models import Perfil
from accounts.views import _qs_escopo
from django.contrib.auth import get_user_model

Usuario = get_user_model()


@pytest.mark.django_db
def test_criar_usuario():
    # usuário comum
    usuario_comum = Usuario.objects.create_user(
        email="usuario@email.com",
        password="12345",
        matricula="111111",
        primeiro_nome="Usuario",
        sobrenome="Comum",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    # administrador
    admin = Usuario.objects.create_user(
        email="admin@email.com",
        password="12345",
        matricula="999999",
        primeiro_nome="Administrador",
        sobrenome="Sistema",
        perfil=Perfil.ADMIN,
        conta_ativada=True,
    )

    # gestor de unidade
    gestor_unidade = Usuario.objects.create_user(
        email="gestor@email.com",
        password="12345",
        matricula="888888",
        primeiro_nome="Gestor",
        sobrenome="Unidade",
        perfil=Perfil.GESTOR_UNIDADE,
        conta_ativada=True,
    )

    # usuário comum não pode cadastrar
    pode_cadastrar_usuario_comum = (
        usuario_comum.perfil in (
            Perfil.ADMIN,
            Perfil.GESTOR_UNIDADE,
        )
    )

    assert pode_cadastrar_usuario_comum is False

    # admin pode cadastrar
    pode_cadastrar_admin = (
        admin.perfil in (
            Perfil.ADMIN,
            Perfil.GESTOR_UNIDADE,
        )
    )

    assert pode_cadastrar_admin is True

    # gestor unidade pode cadastrar
    pode_cadastrar_gestor = (
        gestor_unidade.perfil in (
            Perfil.ADMIN,
            Perfil.GESTOR_UNIDADE,
        )
    )

    assert pode_cadastrar_gestor is True

    # cadastro realizado pelo admin
    if pode_cadastrar_admin:
        usuario_teste = Usuario.objects.create_user(
            email="teste@email.com",
            password="12345",
            matricula="000000",
            primeiro_nome="Teste",
            sobrenome="Usuario",
            perfil=Perfil.SERVIDOR,
            conta_ativada=True,
        )

    verifica = Usuario.objects.get(
        matricula="000000"
    )

    assert verifica.email == "teste@email.com"
    assert verifica.primeiro_nome == "Teste"
    assert verifica.sobrenome == "Usuario"
    assert verifica.perfil == Perfil.SERVIDOR


@pytest.mark.django_db
def test_ler_usuario():
    # cria usuários
    Usuario.objects.create(
        matricula="1",
        email="u1@ufsm.br",
        primeiro_nome="Usuario",
        sobrenome="Um",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    Usuario.objects.create(
        matricula="2",
        email="u2@ufsm.br",
        primeiro_nome="Usuario",
        sobrenome="Dois",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    # cria admin
    admin = Usuario.objects.create(
        matricula="adm",
        email="adm@ufsm.br",
        primeiro_nome="Administrador",
        sobrenome="Sistema",
        perfil=Perfil.ADMIN,
        conta_ativada=True,
    )

    resultado_qs = _qs_escopo(admin)

    # admin consegue ver todos
    assert resultado_qs.count() == 3
    assert admin in resultado_qs

    # cria usuário comum
    u1 = Usuario.objects.create(
        matricula="10",
        email="u10@ufsm.br",
        primeiro_nome="Usuario",
        sobrenome="Dez",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    Usuario.objects.create(
        matricula="20",
        email="u20@ufsm.br",
        primeiro_nome="Usuario",
        sobrenome="Vinte",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    resultado_qs = _qs_escopo(u1)

    # usuário comum vê apenas ele
    assert resultado_qs.count() == 1
    assert resultado_qs.first() == u1


@pytest.mark.django_db
def test_permissao_para_editar_usuario():
    # usuário comum
    usuario_comum = Usuario.objects.create_user(
        email="usuario@email.com",
        password="123456",
        matricula="2024002",
        primeiro_nome="João",
        sobrenome="Silva",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    # administrador
    admin = Usuario.objects.create_user(
        email="admin@email.com",
        password="123456",
        matricula="999999",
        primeiro_nome="Administrador",
        sobrenome="Sistema",
        perfil=Perfil.ADMIN,
        conta_ativada=True,
    )

    # usuário que será editado
    usuario_alvo = Usuario.objects.create_user(
        email="carlos.oliveira@email.com",
        password="123456",
        matricula="2024001",
        primeiro_nome="Carlos",
        sobrenome="Oliveira",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    # usuário comum NÃO pode editar
    pode_editar_usuario_comum = (
        usuario_comum.perfil == Perfil.ADMIN
    )

    assert pode_editar_usuario_comum is False

    # admin PODE editar
    pode_editar_admin = (
        admin.perfil == Perfil.ADMIN
    )

    assert pode_editar_admin is True

    # edição realizada pelo admin
    if pode_editar_admin:
        usuario_alvo.primeiro_nome = "Carlos Eduardo"
        usuario_alvo.sobrenome = "Oliveira Souza"
        usuario_alvo.email = "carlos.eduardo@email.com"
        usuario_alvo.telefone = "(11) 98888-7777"
        usuario_alvo.cargo = "Coordenador Administrativo"
        usuario_alvo.perfil = Perfil.ADMIN
        usuario_alvo.ativo = False

        usuario_alvo.save()

    atualizado = Usuario.objects.get(id=usuario_alvo.id)

    assert atualizado.primeiro_nome == "Carlos Eduardo"
    assert atualizado.sobrenome == "Oliveira Souza"
    assert atualizado.email == "carlos.eduardo@email.com"
    assert atualizado.telefone == "(11) 98888-7777"
    assert atualizado.cargo == "Coordenador Administrativo"
    assert atualizado.perfil == Perfil.ADMIN
    assert atualizado.ativo is False
    assert atualizado.matricula == "2024001"


@pytest.mark.django_db
def test_deletar_usuario():
    usuario_comum = Usuario.objects.create_user(
        email="usuario@email.com",
        password="Senha@123",
        matricula="2024002",
        primeiro_nome="Joao",
        sobrenome="Silva",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    admin = Usuario.objects.create_user(
        email="admin@email.com",
        password="Senha@123",
        matricula="999999",
        primeiro_nome="Administrador",
        sobrenome="Sistema",
        perfil=Perfil.ADMIN,
        conta_ativada=True,
    )

    gestor_unidade = Usuario.objects.create_user(
        email="gestor@email.com",
        password="Senha@123",
        matricula="888888",
        primeiro_nome="Gestor",
        sobrenome="Unidade",
        perfil=Perfil.GESTOR_UNIDADE,
        conta_ativada=True,
    )

    usuario_alvo = Usuario.objects.create_user(
        email="pedro@email.com",
        password="Senha@123",
        matricula="2024001",
        primeiro_nome="Pedro",
        sobrenome="Cassol",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    perfis_com_permissao = (
        Perfil.ADMIN,
        Perfil.GESTOR_UNIDADE,
    )

    pode_deletar_usuario_comum = usuario_comum.perfil in perfis_com_permissao
    assert pode_deletar_usuario_comum is False

    pode_deletar_admin = admin.perfil in perfis_com_permissao
    assert pode_deletar_admin is True

    pode_deletar_gestor_unidade = gestor_unidade.perfil in perfis_com_permissao
    assert pode_deletar_gestor_unidade is True

    if pode_deletar_admin:
        usuario_alvo.soft_delete()

    usuario_alvo.refresh_from_db()

    assert usuario_alvo.ativo is False
    assert usuario_alvo.deleted_at is not None
