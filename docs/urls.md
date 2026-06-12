# URLs Disponíveis

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