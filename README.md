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
| `/logout/` | Autenticado | Encerrar sessão |
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
| `/riscos/` | Autenticado | Listagem dos planos de risco conforme o escopo do usuário |
| `/riscos/novo/` | Autenticado (exceto Servidor) | Criar um novo plano de risco |
| `/riscos/<id>/` | Conforme escopo | Visualização detalhada de um plano de risco |
| `/riscos/<id>/editar/` | Conforme escopo | Editar as seções de um plano de risco |
| `/riscos/<id>/excluir/` | Conforme escopo | Excluir um plano de risco |
| `/riscos/<id>/remanejar/` | Admin / G. Unidade | Trocar o plano para outro setor |
| `/riscos/dashboard/` | Autenticado | Painel com gráficos e matriz de riscos |
| `/riscos/<id>/pdf/` | Conforme escopo | Gerar e baixar o relatório PDF de um plano de risco |
| `/riscos/notificacoes/` | Autenticado | Visualizar as notificações do usuário |
| `/riscos/admin/painel/` | Admin | Painel administrativo dos planos de risco |
| `/riscos/admin/<id>/detalhe/` | Admin | Detalhe técnico de um plano no painel administrativo |
| `/riscos/admin/<id>/deletar/` | Admin | Excluir plano pelo painel administrativo de riscos |
| `/configuracao/` | Admin | Gerenciar Macroprocessos, Desafios PDI e Objetivos PDI |
| `/configuracao/desafio/novo/` | Admin | Cadastrar Desafio PDI |
| `/configuracao/desafio/<id>/editar/` | Admin | Editar Desafio PDI |
| `/configuracao/desafio/<id>/deletar/` | Admin | Excluir Desafio PDI |
| `/configuracao/objetivo/novo/` | Admin | Cadastrar Objetivo PDI |
| `/configuracao/objetivo/<id>/editar/` | Admin | Editar Objetivo PDI |
| `/configuracao/objetivo/<id>/deletar/` | Admin | Excluir Objetivo PDI |
| `/configuracao/macroprocesso/novo/` | Admin | Cadastrar Macroprocesso |
| `/configuracao/macroprocesso/<id>/editar/` | Admin | Editar Macroprocesso |
| `/configuracao/macroprocesso/<id>/deletar/` | Admin | Excluir Macroprocesso |
| `/unidades/` | Admin | Gerenciar Unidades da Instituição |
| `/unidades/nova/` | Admin | Cadastrar Unidade |
| `/unidades/<id>/editar/` | Admin | Editar Unidade |
| `/unidades/<id>/toggle/` | Admin | Ativar/Desativar Unidade |
| `/setores/` | Admin / G. Unidade | Gerenciar Setores |
| `/setores/novo/` | Admin / G. Unidade | Cadastrar Setor |
| `/setores/<id>/editar/` | Admin / G. Unidade | Editar Setor |
| `/setores/<id>/toggle/` | Admin / G. Unidade | Ativar/Desativar Setor |
| `/setores/<id>/vinculos/` | Admin / G. Unidade | Gerenciar vínculos do setor |
| `/setores/<id>/vinculos/add/` | Admin / G. Unidade | Adicionar vínculo ao setor |
| `/vinculos/<id>/encerrar/` | Admin / G. Unidade | Encerrar vínculo de usuário com setor |

## Documentação

<https://ctism-prof-henry.github.io/software-formularios-kanbanda/>

