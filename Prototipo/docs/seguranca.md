
# Permissões e  Segurança

### Resumo da hierarquia de escopo

| Capacidade | Admin | Gestor Unidade | Gestor Setor | Servidor |
|---|:---:|:---:|:---:|:---:|
| Logs de acesso | ✅ | ❌ | ❌ | ❌ |
| Criar usuários | ✅ | ✅ | ❌ | ❌ |
| Alterar perfil | ✅ | ✅ | ❌ | ❌ |
| Config. PDI/Macroprocessos | ✅ | ✅ | ❌ | ❌ |
| Painel global de riscos | ✅ | ❌ | ❌ | ❌ |
| Criar planos de risco | ✅ (qualquer) | ✅ (unidade) | ✅ (setor) | ❌ |
| Remanejar planos | ✅ | ✅ | ❌ | ❌ |
| Ver planos | ✅ (todos) | ✅ (unidade) | ✅ (setor) | ✅ (setor) |

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

