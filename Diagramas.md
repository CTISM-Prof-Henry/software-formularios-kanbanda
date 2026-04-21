<details>
<summary><strong>Código do Diagrama de Uso</strong></summary>
<pre>
    flowchart TD
%% ATORES
    A4["ADMINISTRADOR"]
    A3["GESTOR DA UNIDADE"]
    A2["GESTOR DE SETOR"]
    A1["SERVIDOR/COLABORADOR"]

    subgraph "Sistema de Gestão de Riscos "
        
        
        %% Acesso
        uc1([Autenticar no Sistema])
        
        %%  Administração
        uc6([Administrar Sistema e Usuários])
        
        %% Operação e Cadastro
        uc2([Cadastrar/Editar Plano de Risco])
        ex1([Escalonamento])
        
        %% Listagem e Observação
        uc8([Listar/Filtrar Formulários])
        ex3([Remanejar Riscos entre Setores])
        uc7([Registrar Observações])
        
        %% Monitoramento e Saída
        uc3([Monitorar Resultados e Planos])
        ex2([Notificar Planos Atrasados])
        uc4([Visualizar Dashboards])
        uc5([Gerar Relatórios e PDF])
    end

    %% Relacionamentos de Inclusão 
    uc2 -. include .-> uc1
    uc3 -. include .-> uc1
    uc4 -. include .-> uc1
    uc5 -. include .-> uc1
    uc8 -. include .-> uc1

    %% Relacionamentos de Extensão 
    ex1 -. extend .-> uc2
    ex2 -. extend .-> uc3
    ex3 -. extend .-> uc8

    %% ligação: Administrador
    A4 --> uc6
    A4 --> uc5

    %% ligação: Gestor da Unidade
    A3 --> uc2
    A3 --> uc4
    A3 --> uc8
    A3 --> ex3

    %% ligação: Gestor de Setor
    A2 --> uc2
    A2 --> uc3
    A2 --> uc4
    A2 --> uc5

    %% Ligação: Servidor
    A1 --> uc8
    A1 --> uc7
    A1 --> uc1
</pre>
</details>

```mermaid
flowchart TD
%% ATORES
    A4["ADMINISTRADOR"]
    A3["GESTOR DA UNIDADE"]
    A2["GESTOR DE SETOR"]
    A1["SERVIDOR/COLABORADOR"]

    subgraph "Sistema de Gestão de Riscos "
        
        
        %% Acesso
        uc1([Autenticar no Sistema])
        
        %%  Administração
        uc6([Administrar Sistema e Usuários])
        
        %% Operação e Cadastro
        uc2([Cadastrar/Editar Plano de Risco])
        ex1([Escalonamento])
        
        %% Listagem e Observação
        uc8([Listar/Filtrar Formulários])
        ex3([Remanejar Riscos entre Setores])
        uc7([Registrar Observações])
        
        %% Monitoramento e Saída
        uc3([Monitorar Resultados e Planos])
        ex2([Notificar Planos Atrasados])
        uc4([Visualizar Dashboards])
        uc5([Gerar Relatórios e PDF])
    end

    %% Relacionamentos de Inclusão 
    uc2 -. include .-> uc1
    uc3 -. include .-> uc1
    uc4 -. include .-> uc1
    uc5 -. include .-> uc1
    uc8 -. include .-> uc1

    %% Relacionamentos de Extensão 
    ex1 -. extend .-> uc2
    ex2 -. extend .-> uc3
    ex3 -. extend .-> uc8

    %% ligação: Administrador
    A4 --> uc6
    A4 --> uc5

    %% ligação: Gestor da Unidade
    A3 --> uc2
    A3 --> uc4
    A3 --> uc8
    A3 --> ex3

    %% ligação: Gestor de Setor
    A2 --> uc2
    A2 --> uc3
    A2 --> uc4
    A2 --> uc5

    %% Ligação: Servidor
    A1 --> uc8
    A1 --> uc7
    A1 --> uc1
```

<details>
<summary><strong>Código do diagrama</strong></summary>
<pre>
    
</pre>
</details>

```mermaid
```

<details>
<summary><strong>Código do diagrama</strong></summary>
<pre>
classDiagram

class Perfil {
    +int id
    +String nome
    +String permissoes
}

class Usuario {
    +int id
    +String nome
    +String email
    +String senha
    +String foto
    +boolean ativo
    +int perfil_id
}

class Unidade {
    +int id
    +String nome
    +String tipo
}

class Setor {
    +int id
    +String nome
    +int unidade_id
}

class UsuarioSetor {
    +int usuario_id
    +int setor_id
}

Perfil "1" --> "N" Usuario
Unidade "1" --> "N" Setor
Usuario "1" --> "N" UsuarioSetor
Setor "1" --> "N" UsuarioSetor

class PlanoDeRisco {
    +int id
    +String status
    +Date data_criacao
    +Date data_ultima_atualizacao
    +int versao
    +Date excluido_em
    +int usuario_criador_id
    +int setor_id
}

Setor "1" --> "N" PlanoDeRisco
Usuario "1" --> "N" PlanoDeRisco : cria

class DesafioPDI {
    +int id
    +int numero
    +String descricao
}

class Macroprocesso {
    +int id
    +String nome
    +int desafio_id
}

class ObjetivoPDI {
    +int id
    +String codigo
    +String descricao
    +int desafio_id
}

class CategoriaRisco {
    +int id
    +String nome
}

DesafioPDI "1" --> "N" Macroprocesso
DesafioPDI "1" --> "N" ObjetivoPDI

class IdentificacaoRisco {
    +int id
    +int plano_id
    +int categoria_id
    +String descricao_evento
    +String causas
    +String consequencias
    +int macroprocesso_id   
    +int objetivo_pdi_id
}

PlanoDeRisco "1" *-- "1" IdentificacaoRisco
CategoriaRisco "1" --> "N" IdentificacaoRisco
IdentificacaoRisco --> Macroprocesso
IdentificacaoRisco --> ObjetivoPDI

class EscalaProbabilidade {
    +int id
    +String nivel
    +int valor
}

class EscalaImpacto {
    +int id
    +String nivel
    +int valor
}

class AvaliacaoRisco {
    +int id
    +int plano_id
    +int probabilidade_id
    +int impacto_id
    +int risco_inerente
    +String nivel_risco_inerente
    +String eficacia_controles
    +String descricao_controles
    +int risco_residual
    +String nivel_risco_residual
}

PlanoDeRisco "1" *-- "1" AvaliacaoRisco
EscalaProbabilidade "1" --> "N" AvaliacaoRisco
EscalaImpacto "1" --> "N" AvaliacaoRisco

class TratamentoRisco {
    +int id
    +int plano_id
    +String resposta
    +String tipo_acao
    +String descricao_acao
    +String situacao
    +Date data_inicio
    +Date data_conclusao_prevista
    +int responsavel_id
    +String observacoes
    +String resultados_observados
    +String analise_critica
}

class TratamentoParceiro {
    +int tratamento_id
    +int usuario_id
}

PlanoDeRisco "1" *-- "0..1" TratamentoRisco
TratamentoRisco "1" --> "N" TratamentoParceiro
Usuario "1" --> "N" TratamentoParceiro

class HistoricoAlteracao {
    +int id
    +int plano_id
    +int usuario_id
    +String campo_alterado
    +String valor_anterior
    +String valor_novo
    +DateTime data_hora
}

class Notificacao {
    +int id
    +int usuario_id
    +int plano_id
    +String tipo
    +String mensagem
    +boolean lida
    +DateTime data_hora
}

PlanoDeRisco "1" --> "N" HistoricoAlteracao
Usuario "1" --> "N" HistoricoAlteracao : realiza

PlanoDeRisco "1" --> "N" Notificacao
Usuario "1" --> "N" Notificacao
</pre>
</details>

![diagramaClasse.png](diagramaClasse.png)