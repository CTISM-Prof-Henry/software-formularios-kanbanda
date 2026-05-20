import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Perfil
from ..views import _qs_escopo

Usuario = get_user_model()


@pytest.fixture()
def usuario_comum():
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
    return Usuario.objects.create_user(
        email="teste@email.com",
        password="12345",
        matricula="000000",
        primeiro_nome="Teste",
        sobrenome="Usuario",
        perfil=Perfil.SERVIDOR,
        conta_ativada=True,
    )

@pytest.fixture()
def setor_teste():
    from organizacional.models import Unidade, Setor
    unidade = Unidade.objects.create(nome="Unidade Teste", sigla="UT", tipo="ORGAO")
    return Setor.objects.create(unidade=unidade, nome="Setor Teste", sigla="ST")


#TESTES DE CRUD USUÁRIO

@pytest.mark.django_db
def test_crud_criar_usuario(usuario_comum, usuario_adm, usuario_gestor):
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
    client.force_login(usuario_adm) #entra como adm para acessar a pag de usuarios
    
    url = reverse("lista_usuarios") #gera a url para acessar a lista
    response = client.get(url) #requisição get

    assert response.status_code == 200 #verifica se a resposta foi bem sucedida(200)
    assert "usuarios" in response.context #verifica se usuarios está na resposta
    
    usuarios_na_tela = response.context["usuarios"] #pega os usuarios que retornou
    assert usuario_teste in usuarios_na_tela #verifica se o usuario teste esta na lista

@pytest.mark.django_db
def test_endpoint_cadastro_usuario(client, usuario_adm):
    pass

@pytest.mark.django_db
def test_endpoint_editar_usuario(client, usuario_adm, usuario_teste, setor_teste):
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
def test_endpoint_desativa_usuario(client, usuario_adm, usuario_teste):  #cliente para simular requisições
    usuario_teste.ativo = True  #garante que o usuário começa ativo
    usuario_teste.save(update_fields=["ativo"])  #salva no banco apenas o campo ativo

    client.force_login(usuario_adm)  #simula o login do administrador

    url = reverse("toggle_ativo", kwargs={"pk": usuario_teste.pk})  #gera a URL do endpoint usando o id do usuário
    response = client.post(url)  #faz uma requisição POST para desativar o usuário

    usuario_teste.refresh_from_db()  #atualiza o objeto com os dados salvos no banco

    assert response.status_code == 302  #verifica se a view redirecionou após a ação
    assert response.url == reverse("lista_usuarios")  #verifica se o redirecionamento foi para a lista de usuários
    assert usuario_teste.ativo is False  #confirma que o usuário foi desativado
