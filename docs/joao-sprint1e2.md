# Relatório Individual de Contribuição — Sprints 1 e 2 (E5 / E6)

**Aluno:** João Gabriel Cardoso Martarello  
**RA:** 2840482421028  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Desenvolvedor Backend / Regras de Negócio e Validações  
**Período:** 21/08/2026 a 14/10/2026  
**Sprint:** 1 e 2 (E5 / E6)  

---

## 1. Atividades Realizadas nas Sprints

Nestas Sprints 1 e 2, atuei como responsável pelo desenvolvimento do backend de cadastros, validação de regras de domínio, cálculo financeiro de alta precisão e serviços transacionais para manipulação de itens de Ordem de Serviço:

- **Validações de Domínio e Normalização de Dados (H03, H04):**
  - Implementação de validadores e normalizadores para CPF em `core/validators.py`, garantindo cálculo oficial de dígitos verificadores e armazenamento sem pontuação.
  - Implementação de validadores e normalizadores para Placas de Veículos em `core/validators.py`, suportando padrão tradicional (`ABC-1234`) e Mercosul (`ABC1D23`), normalizando para formato sem hífen e em maiúsculas.

- **Cálculo Financeiro e Descontos com Alta Precisão (H11):**
  - Desenvolvimento da função de negócio central `calcular_totais` em `core/calculos.py` utilizando o tipo nativo `Decimal` do Python para prevenir imprecisões de ponto flutuante.
  - Regra de validação estrita do desconto percentual (intervalo permitido de 0% a 100%), rejeitando strings inválidas, percentuais negativos ou superiores a 100%.
  - Totalização de subtotais por item e cálculo do valor final líquido com arredondamento monetário bancário padrão `ROUND_HALF_UP` em duas casas decimais.

- **Serviços Transacionais de Manipulação de Itens na OS (H13, H14):**
  - Implementação das funções de serviço `incluir_item`, `remover_item` e `alterar_desconto` em `core/services.py` com garantia de atomicidade via `@transaction.atomic`.
  - Associação de peças e serviços à Ordem de Serviço com congelamento do preço unitário histórico (`preco_unitario_historico`), garantindo integridade contábil mesmo se o valor de catálogo for alterado posteriormente.
  - Bloqueio de edição para Ordens de Serviço que não estejam no status "Pendente" e recálculo automático do subtotal e total da OS após cada operação.
  - Respeito à regra de não efetuar baixa prematura de estoque no momento da inclusão do item (a baixa atômica de estoque foi reservada para a aprovação da OS na Sprint 3).

- **Formulários Padronizados com Feedback de Erro (H22):**
  - Construção de `ClienteForm` e `VeiculoForm` em `core/forms.py` com estilização Bootstrap 5.
  - Retenção dos dados válidos e exibição contextual de erros por campo (`is-invalid` e mensagens de erro do formulário).
  - Customização de `AuthenticationForm` em `core/forms_login.py` para compatibilidade com o layout visual de autenticação.

- **Suíte de Testes Automatizados Unitários e de Integração:**
  - Criação de testes unitários abrangentes cobrindo cálculos matemáticos, limites de desconto, entradas inválidas e validação de CPF e Placa.
  - Criação de testes de integração para controllers de cadastro de cliente, veículo e operações de itens em `core/tests/test_cadastros_e_ordens.py`.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H03** (Cadastro de Clientes) | Validação matemática de CPF, normalização e formulário Django | Concluída |
| **H04** (Cadastro de Veículos) | Validação de Placas (Mercosul/antiga) e normalização | Concluída |
| **H11** (Desconto e Totalização) | Cálculo decimal com `ROUND_HALF_UP` e validação estrita (0-100%) | Concluída |
| **H13** (Associação N:N de Peças) | Serviços de inclusão/remoção com preço histórico congelado | Concluída |
| **H14** (Associação N:N de Serviços)| Serviços de inclusão/remoção de serviços na OS | Concluída |
| **H22** (Validações de Formulário) | Formulários Django com retenção de dados e erros por campo | Concluída |

---

## 3. Evidências Técnicas (PRs e Commits)

- `Commit 82aa9e5` — Implementação dos cálculos decimais, validadores, formulários e suite de testes
- `PR #02` — Integração da branch `joao-sprint1e2` ao repositório principal
- Arquivos de código produzidos: `core/calculos.py`, `core/validators.py`, `core/services.py`, `core/forms.py` e `core/tests/test_cadastros_e_ordens.py`

---

## 4. Autoavaliação e Lições Aprendidas

A separação das regras de negócio em módulos puros (`calculos.py` e `validators.py`) facilitou a escrita de testes unitários rápidos e determinísticos sem dependência da infraestrutura de banco de dados. O uso do tipo `Decimal` preveniu erros clássicos de arredondamento em somas financeiras, assegurando total aderência aos critérios de aceitação e aos casos de teste da disciplina.
