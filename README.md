# RiskShield — Sistema de Gestão de Riscos da UFSM

Projeto de Engenharia de Software de sistema web Django para identificação, análise e tratamento de riscos da **Universidade Federal de Santa Maria**.

---

## Instalação (PowerShell)

```bash
#Entrar na pasta do código
cd .\<seulocal>\software-formularios-kanbanda-main\software-formularios-kanbanda-main\risco_ufsm

#Criar e ativar o ambiente virtual
python3 -m venv venv
Set-ExecutionPolicy Unrestricted -Scope Process
. venv/Scripts/Activate.ps1

# Instalar dependências
python -m pip install -r requirements.txt

# Migrations
python manage.py migrate

# Criar primeiro administrador
python manage.py criar_admin_inicial

# Rodar
python manage.py runserver
```

---

## Perfis e Permissões

| Funcionalidade | Admin | G. Unidade | G. Setor | Servidor |
|---|:---:|:---:|:---:|:---:|
| Criar usuários | ✅ | ✅ | ❌ | ❌ |
| Editar usuários | ✅ | ✅ | ✅** | ❌ |
| Ativar/desativar | ✅ | ✅ | ❌ | ❌ |
| Listar usuários | ✅ | ✅ | ✅** | ❌ |
| Logs de acesso | ✅ | ❌ | ❌ | ❌ |
| Meu perfil / senha | ✅ | ✅ | ✅ | ✅ |
| Painel | ✅ | ✅ | ✅ | ✅ |

\*\* Restrito ao próprio setor

---

## Fluxo de Cadastro (sem acesso público)

```
Admin/Gestor cria usuário
        ↓
Sistema envia e-mail com link único (token UUID, 48h)
        ↓
Usuário clica no link → cria senha (8+ chars, maiúscula, minúscula, número, especial)
        ↓
Conta ativada → pode fazer login
```

---

## Segurança Implementada

- **Senhas criptografadas** (PBKDF2 + SHA256, Django padrão)
- **CSRF** em todos os formulários POST
- **Sessão** expira em 30 minutos de inatividade
- **Brute force**: bloqueia IP após 5 tentativas falhas por 15 minutos
- **Token de ativação**: UUID v4, expira em 48h, uso único
- **Token de recuperação**: UUID v4, expira em 15 minutos, uso único
- **Nunca revela** se usuário existe na recuperação de senha
- **Soft delete**: nenhum registro é apagado fisicamente
- **Logs imutáveis**: LogAcesso e LogAlteracao bloqueiam `.delete()`
- **Histórico completo** via `django-simple-history` em Usuario, Unidade, Setor, UsuarioSetor
- **Scoping organizacional**: cada perfil vê apenas os dados do seu escopo

---

## URLs Disponíveis

| URL | Acesso | Descrição |
|---|---|---|
| `/login/` | Público | Tela de login |
| `/recuperar-senha/` | Público | Solicitar redefinição |
| `/redefinir-senha/<token>/` | Token válido | Criar nova senha |
| `/ativar-conta/<token>/` | Token válido | Ativação inicial |
| `/painel/` | Autenticado | Painel por perfil |
| `/usuarios/` | Admin/G.Unidade/G.Setor | Listar usuários |
| `/usuarios/novo/` | Admin/G.Unidade | Cadastrar usuário |
| `/usuarios/<id>/editar/` | Conforme escopo | Editar usuário |
| `/usuarios/<id>/toggle-ativo/` | Admin/G.Unidade | Ativar/Desativar |
| `/usuarios/<id>/reenviar-ativacao/` | Admin/G.Unidade | Reenviar e-mail |
| `/meu-perfil/` | Autenticado | Dados pessoais e senha |
| `/logs/acesso/` | Admin | Auditoria de acessos |
| `/admin/` | Admin | Painel administrativo |

## Documentação

<https://ctism-prof-henry.github.io/software-formularios-kanbanda/>

