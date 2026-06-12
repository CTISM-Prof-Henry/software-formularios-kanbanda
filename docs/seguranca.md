
# Permissões e  Segurança

### Perfis e Permissões do Sistema

| Funcionalidade | Admin | G. Unidade | G. Setor | Servidor |
|---|:---:|:---:|:---:|:---:|
| Criar usuários | ✅ | ✅ | ❌ | ❌ |
| Editar usuários | ✅ | ✅ | ✅[^1] | ❌ |
| Ativar/desativar | ✅ | ✅ | ❌ | ❌ |
| Listar usuários | ✅ | ✅ | ✅[^1] | ❌ |
| Logs de acesso | ✅ | ❌ | ❌ | ❌ |
| Meu perfil / senha | ✅ | ✅ | ✅ | ✅ |
| Painel | ✅ | ✅ | ✅ | ✅ |

[^1]: **Restrição:** Restrito ao próprio setor do gestor.

---

### Segurança 

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

