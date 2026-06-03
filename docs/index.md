# RiskShield — Gestão de Riscos da UFSM

Projeto de Engenharia de Software de sistema web Django na Universidade Federal de Santa Maria.

# Objetivo
Este projeto está sendo desenvolvido na disciplina de Engenharia de Software, com o objetivo de fornecer uma plataforma web para o registro e monitoramento de riscos no que diz respeito a parte acadêmica e administrativa da UFSM.

## Fluxo de Cadastro

 **Admin/Gestor cria usuário**
  <br> ↓

 **Sistema envia e-mail com link único (token UUID, 48h)**
   <br> ↓

 **Usuário clica no link → cria senha (8+ chars, maiúscula, minúscula, número, especial)**
   <br> ↓

 **Conta ativada → pode fazer login**
  