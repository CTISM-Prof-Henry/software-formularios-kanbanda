# URLs Disponíveis

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
