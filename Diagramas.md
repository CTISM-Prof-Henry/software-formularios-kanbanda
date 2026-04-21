<details>
<summary><strong>Código do diagrama</strong></summary>
<pre>

    flowchart TD
    actor1["👤 Usuário"]
    actor2["👤 Administrador"]

    subgraph Sistema
        uc1([Realizar Login])
        uc2([Gerar relatório])
        uc3([Gerenciar usuários])
    end

    actor1 --> uc1
    actor1 --> uc2
    actor2 --> uc3
    actor2 --> uc2
    actor2 --> uc1
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