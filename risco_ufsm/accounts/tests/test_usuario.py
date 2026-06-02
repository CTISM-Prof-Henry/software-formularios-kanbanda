'''
Testes para o modelo de Usuário e suas views associadas.
Esses testes cobrem as operações de CRUD (Criar, Ler, Editar, Deletar)
para o modelo de Usuário, bem como os endpoints relacionados à gestão
de usuários como a listagem, edição e desativação de usuários.
'''
# pylint: disable=redefined-outer-name,no-member

# tive que desabilitar o no-member para acessar os campos do modelo de usuário
# e o redefined-outer-name para usar os nomes dos fixtures como parâmetros dos testes

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from organizacional.models import Setor, Unidade
from ..models import Perfil
from ..views import _qs_escopo

Usuario = get_user_model()


@pytest.fixture()
def usuario_comum():
    """Cria um usuário comum para testes."""
    return Usuario.objects.create_user(
        email="usuario@email.com",
        password="12345",
        matricula="111111",
        primeiro_nome="Usuario",
        sobrenome="Comum",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )


@pytest.fixture()
def usuario_adm():
    """Cria um usuário administrador para testes."""
    return Usuario.objects.create_user(
        email="admin@email.com",
        password="12345",
        matricula="999999",
        primeiro_nome="Administrador",
        sobrenome="Sistema",
        perfil=Perfil.ADMIN,
        conta_ativada=True,
    )


@pytest.fixture()
def usuario_gestor():
    """Cria um usuário gestor para testes."""
    return Usuario.objects.create_user(
        email="gestor@email.com",
        password="12345",
        matricula="888888",
        primeiro_nome="Gestor",
        sobrenome="Unidade",
        perfil=Perfil.GESTOR_UNIDADE,
        conta_ativada=True,
    )


@pytest.fixture()
def usuario_teste():
    """Cria um usuário de teste para interações."""
    return Usuario.objects.create_user(
        email="teste@email.com",
        password="12345",
        matricula="000000",
        primeiro_nome="Teste",
        sobrenome="Usuario",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

# pylint: disable=no-member
@pytest.fixture()
def setor_teste():
    """Cria um setor de teste vinculado a uma unidade."""
    unidade = Unidade.objects.create(
        nome="Unidade Teste",
        sigla="UT",
        tipo="ORGAO",
    )
    return Setor.objects.create(
        unidade=unidade,
        nome="Setor Teste",
        sigla="ST",
    )


# TESTES DE CRUD USUÁRIO
@pytest.mark.django_db
def test_crud_criar_usuario(usuario_comum, usuario_adm, usuario_gestor):
    """Verifica as permissões de criação e criação de um novo usuário."""
    pode_cadastrar_usuario_comum = usuario_comum.perfil in (
        Perfil.ADMIN,
        Perfil.GESTOR_UNIDADE,
    )

    assert pode_cadastrar_usuario_comum is False

    pode_cadastrar_admin = usuario_adm.perfil in (
        Perfil.ADMIN,
        Perfil.GESTOR_UNIDADE,
    )

    assert pode_cadastrar_admin is True

    pode_cadastrar_gestor = usuario_gestor.perfil in (
        Perfil.ADMIN,
        Perfil.GESTOR_UNIDADE,
    )

    assert pode_cadastrar_gestor is True

    if pode_cadastrar_admin:
        Usuario.objects.create_user(
            email="novo@email.com",
            password="12345",
            matricula="222222",
            primeiro_nome="Novo",
            sobrenome="Usuario",
            perfil=Perfil.SERVIDOR,
            conta_ativada=True,
        )

    verifica = Usuario.objects.get(matricula="222222")

    assert verifica.email == "novo@email.com"
    assert verifica.primeiro_nome == "Novo"
    assert verifica.sobrenome == "Usuario"
    assert verifica.perfil == Perfil.SERVIDOR


@pytest.mark.django_db
def test_crud_ler_usuario(usuario_adm, usuario_teste):
    """Verifica leitura de usuários no escopo correto."""
    Usuario.objects.create_user(
        matricula="1",
        email="u1@ufsm.br",
        password="12345",
        primeiro_nome="Usuario",
        sobrenome="Um",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    Usuario.objects.create_user(
        matricula="2",
        email="u2@ufsm.br",
        password="12345",
        primeiro_nome="Usuario",
        sobrenome="Dois",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

    resultado_qs = _qs_escopo(usuario_adm)

    assert resultado_qs.count() == 4
    assert usuario_adm in resultado_qs
    assert usuario_teste in resultado_qs

    resultado_qs = _qs_escopo(usuario_teste)

    assert resultado_qs.count() == 1
    assert resultado_qs.first() == usuario_teste


@pytest.mark.django_db
def test_crud_editar_usuario(usuario_comum, usuario_adm, usuario_teste):
    """Verifica edição de usuário por perfis com permissão."""
    pode_editar_usuario_comum = usuario_comum.perfil == Perfil.ADMIN
    assert pode_editar_usuario_comum is False

    pode_editar_admin = usuario_adm.perfil == Perfil.ADMIN
    assert pode_editar_admin is True

    if pode_editar_admin:
        usuario_teste.primeiro_nome = "Carlos Eduardo"
        usuario_teste.sobrenome = "Oliveira Souza"
        usuario_teste.email = "carlos.eduardo@email.com"
        usuario_teste.telefone = "(11) 98888-7777"
        usuario_teste.cargo = "Coordenador Administrativo"
        usuario_teste.perfil = Perfil.ADMIN
        usuario_teste.ativo = False
        usuario_teste.save()

    atualizado = Usuario.objects.get(id=usuario_teste.id)

    assert atualizado.primeiro_nome == "Carlos Eduardo"
    assert atualizado.sobrenome == "Oliveira Souza"
    assert atualizado.email == "carlos.eduardo@email.com"
    assert atualizado.telefone == "(11) 98888-7777"
    assert atualizado.cargo == "Coordenador Administrativo"
    assert atualizado.perfil == Perfil.ADMIN
    assert atualizado.ativo is False
    assert atualizado.matricula == "000000"


@pytest.mark.django_db
def test_crud_deletar_usuario(usuario_comum, usuario_adm, usuario_gestor, usuario_teste):
    """Verifica exclusão lógica de usuário por perfil autorizado."""
    perfis_com_permissao = (
        Perfil.ADMIN,
        Perfil.GESTOR_UNIDADE,
    )

    pode_deletar_usuario_comum = usuario_comum.perfil in perfis_com_permissao
    assert pode_deletar_usuario_comum is False

    pode_deletar_admin = usuario_adm.perfil in perfis_com_permissao
    assert pode_deletar_admin is True

    pode_deletar_gestor_unidade = usuario_gestor.perfil in perfis_com_permissao
    assert pode_deletar_gestor_unidade is True

    if pode_deletar_admin:
        usuario_teste.soft_delete(usuario_adm)

    usuario_teste.refresh_from_db()

    assert usuario_teste.ativo is False
    assert usuario_teste.deleted_at is not None

#TESTES DE ENDPOINTS DE USUÁRIO

@pytest.mark.django_db
def test_endpoint_lista_usuarios(client, usuario_adm, usuario_teste):
    """Verifica se a lista de usuários está disponível ao administrador."""
    client.force_login(usuario_adm)
    url = reverse("lista_usuarios")
    response = client.get(url)

    assert response.status_code == 200
    assert "usuarios" in response.context
    usuarios_na_tela = response.context["usuarios"]
    assert usuario_teste in usuarios_na_tela

@pytest.mark.django_db
def test_endpoint_editar_usuario(client, usuario_adm, usuario_teste, setor_teste):
    """Verifica edição de usuário pelo endpoint apropriado."""
    client.force_login(usuario_adm)

    url = reverse("editar_usuario", kwargs={"pk": usuario_teste.pk})

    dados_form = {
        "primeiro_nome": "Carlos Eduardo",
        "sobrenome": "Oliveira Souza",
        "email": "carlos.eduardo@email.com",
        "perfil": Perfil.SERVIDOR,
        "setores": [setor_teste.pk],
    }

    response = client.post(url, data=dados_form)

    usuario_teste.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse("lista_usuarios")
    assert usuario_teste.primeiro_nome == "Carlos Eduardo"
    assert usuario_teste.sobrenome == "Oliveira Souza"
    assert usuario_teste.email == "carlos.eduardo@email.com"

@pytest.mark.django_db
# cliente para simular requisições
def test_endpoint_desativa_usuario(client, usuario_adm, usuario_teste):
    """Verifica desativação de usuário via endpoint pelo administrador."""
    usuario_teste.ativo = True
    usuario_teste.save(update_fields=["ativo"])

    client.force_login(usuario_adm)

    url = reverse("toggle_ativo", kwargs={"pk": usuario_teste.pk})
    response = client.post(url)

    usuario_teste.refresh_from_db()

    assert response.status_code == 302
    assert response.url == reverse("lista_usuarios")
    assert usuario_teste.ativo is False
