# Relatório Individual de Contribuição — Sprint 2 (E6)

**Aluno:** Rodrigo de Azevedo Junior  
**RA:** 2840482421044  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Desenvolvedor Frontend / Configuração Django  
**Período:** 23/09/2026 a 14/10/2026  
**Sprint:** 2 (E6)  

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 2, concentrei minhas atividades no desenvolvimento da interface dinâmica de orçamentos, cálculo de valores em tempo real, suporte aos relacionamentos N:N na interface e componentes de gestão de estoque:

- **Interface de Montagem de Orçamento Dinâmico (H10, H13, H14):**
  - Desenvolvimento da interface `templates/orcamentos/orcamento_form.html` com seleção facilitada de Cliente e Veículo associado.
  - Implementação de script em JavaScript modular (`static/js/orcamento.js`) para adição e remoção dinâmica de múltiplas linhas de peças e serviços na tabela (suporte ao relacionamento N:N).
  - Otimização da ergonomia visual da tela para cumprir o critério de montagem rápida de orçamento (meta de atendimento em menos de 5 minutos).

- **Cálculo de Desconto e Totais em Tempo Real (H11):**
  - Implementação das funções no frontend para escuta de eventos nos campos de quantidade, valor unitário e percentual de desconto.
  - Validação estrita do desconto (intervalo permitido de 0% a 100%), rejeitando entradas inválidas.
  - Atualização automática dos subtotais por linha e do valor líquido final da OS, com formatação monetária padrão BRL (duas casas decimais e fonte JetBrains Mono).

- **Fluxo Visual de Conversão de Orçamento em OS (H12):**
  - Criação do botão e modal de confirmação para converter o orçamento finalizado em Ordem de Serviço com status inicial "Pendente".
  - Desativação de múltiplos cliques no botão para evitar conversões duplicadas no servidor.

- **Componentes de Ajuste de Estoque e Exclusão Segura (H08, H09):**
  - Atualização da tabela de peças com modal rápido para ajuste manual de saldo em estoque por Dono/Gerente, com bloqueio visual de reduções que gerem saldo negativo.
  - Inserção de feedback visual e bloqueio na ação de exclusão caso a peça possua vínculo registrado em Ordens de Serviço.

- **Manutenção do Deploy Contínuo (H24):**
  - Atualização do ambiente de homologação no Render com as novas rotas, migrações de banco da Sprint 2 e verificação de integridade dos assets JavaScript.

- **Validação Automatizada com Testes (H08, H09, H10, H11, H12):**
  - Execução e validação dos testes automatizados de ajuste de saldo não-negativo, bloqueio de exclusão vinculada e conversão atômica de orçamentos em OS Pendente em `core/tests/test_sprint1_sprint2.py`.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H08** (Ajuste de Estoque) | Modal de atualização de saldo com validação não-negativa | Concluída |
| **H09** (Exclusão Segura de Peças) | Interface com alertas e bloqueio de exclusão vinculada | Concluída |
| **H10** (Montagem de Orçamento) | Interface dinâmica de seleção de itens e quantidades | Concluída |
| **H11** (Desconto e Total) | Script JS para cálculo de subtotais e desconto em tempo real | Concluída |
| **H12** (Conversão de Orçamento em OS)| Ação e modal de confirmação de conversão em OS Pendente | Concluída |
| **H13** (Associação N:N de Peças) | Tabela dinâmica de inserção de múltiplas peças com quantidade | Concluída |
| **H14** (Associação N:N de Serviços)| Tabela dinâmica de inserção de múltiplos serviços | Concluída |

---

## 3. Evidências Técnicas (PRs e Commits)

- `PR #14` — Interface de ajuste de estoque de peças e regras visuais de exclusão protegida
- `PR #17` — Estrutura de template `orcamento_form.html` e componentes de seleção de veículos
- `PR #20` — Implementação do script JS modular de cálculo dinâmico de itens, desconto e totalização
- `PR #22` — Fluxo visual de conversão de orçamento para OS Pendente e prevenção de duplo clique
- `PR #25` — Sincronização e deploy contínuo das novas funcionalidades no Render
- `Suíte de Testes` — Testes automatizados em `core/tests/test_sprint1_sprint2.py` executados com 100% de sucesso

---

## 4. Autoavaliação e Lições Aprendidas

A manipulação dinâmica dos itens de peças e serviços via JavaScript permitiu que o atendente monte orçamentos completos de forma ágil sem recarregar a página, atendendo ao requisito de tempo da história H10. O alinhamento dos campos enviados via POST com os modelos N:N criados pela equipe de banco garantiu o congelamento correto dos preços históricos e a integridade de dados na conversão para Ordem de Serviço Pendente.
