# URLs Disponíveis

| URL | Acesso | Descrição |

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
| `/riscos/` | Autenticado | Listagem de todos os planos de risco|
| `/riscos/novo/` | Autenticado (exceto Servidor) | Criar um novo plano de risco |
| `/riscos/<id>/` | Conforme escopo | Visualização detalhada de um plano de risco |
| `/riscos/<id>/editar/` | Conforme escopo | Editar as seções de um plano de risco |
| `/riscos/<id>/excluir/` | Conforme escopo | Excluir um plano de risco |
| `/riscos/<id>/remanejar/` | Admin / G. Unidade | Trocar o plano para outro setor |
| `/riscos/dashboard/` | Autenticado (exceto Servidor) | Painel com gráficos e matriz de riscos |
| `/riscos/<id>/pdf/` | Conforme escopo | Gerar relatório em PDF de um plano |
| `/riscos/notificacoes/` | Autenticado | Visualizar notificações |
| `/configuracao/` | Admin | Gerenciar Macroprocessos, Desafios PDI e Objetivos PDI |
| `/organizacional/unidades/` | Admin | Gerenciar Unidades da Instituição |
| `/organizacional/setores/` | Admin / G. Unidade | Gerenciar Setores e vínculos |
