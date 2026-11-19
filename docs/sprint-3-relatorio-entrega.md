# Relatório de Entrega da Sprint 3 (E7) — Documento Capa

**Projeto:** Nova Mecânica — Sistema de Gestão para Oficina Mecânica  
**Disciplina:** Laboratório de Software 3 (Laboratório de Engenharia de Software) — Trilha B  
**Instituição:** FATEC Ribeirão Preto — Curso de Análise e Desenvolvimento de Sistemas (ADS)  
**Sprint:** 3 (E7) — Aprovação Atômica de OS, Baixa de Estoque, Histórico por Placa e Painel do Mecânico  
**Período da Sprint:** 15/10/2026 a 04/11/2026  
**Pontuação Planejada vs. Entregue:** 15 Story Points / 15 Story Points (100%)  
**URL de Produção / Homologação (Render):** `https://nova-mecanica.onrender.com`  
**Repositório Oficial:** `https://github.com/YoshiStoshi/Nova-Mecanica`  

---

## 1. Identificação da Equipe Oficial

| Integrante | RA | Papel Principal na Sprint 3 | Relatório Individual |
|---|---|---|---|
| **Rodrigo de Azevedo Junior** | `2840482421044` | Telas de Aprovação de OS (`aprovar_os.html`), Histórico por Placa (`historico_placa.html`), Fila do Mecânico (`os_dia.html`), Integração de Views e Deploy | [sprint-3-contribuicao-rodrigo.md](sprint-3-contribuicao-rodrigo.md) |
| **Felipe Delchiaro Malzoni** | `2840482421025` | Backend Transacional de Aprovação com `select_for_update`, Confirmação de Uso sem Nova Baixa e Conclusão de OS (`core/views.py`) | [sprint-3-contribuicao-felipe.md](sprint-3-contribuicao-felipe.md) |
| **João Gabriel Cardoso Martarello** | `2840482421028` | Painel do Mecânico com fila operacional do dia (`H16`), conclusão da OS com data/hora (`H18`) e testes automatizados | [sprint-3-contribuicao-joao.md](sprint-3-contribuicao-joao.md) |
| **Carlos Chen** | `2840482421030` | Evolução do Modelo Relacional (`estoque_baixado`, `aprovada_em`, `data_conclusao`, `quantidade_utilizada`), Concorrência (`select_for_update`) e Integridade no Banco | [sprint-2-contribuicao-chen.md](sprint-2-contribuicao-chen.md) |

---

## 2. Escopo da Sprint 3: Planejado vs. Entregue (15 Pontos)

| ID | História de Usuário (Backlog E2) | Pontos | Planejado | Entregue | Evidência Principal no Repositório |
|---|---|---|---|---|---|
| **H05** | Consulta rápida ($< 3$s) do histórico completo de manutenção do veículo pela placa | 3 pts | Sim | **100% Concluída** | `core/views.py` (`historico_placa`), `templates/veiculos/historico_placa.html` |
| **H15** | Aprovação de OS pelo Dono/Gerente com verificação e baixa atômica de estoque (`select_for_update`) | 5 pts | Sim | **100% Concluída** | `core/views.py` (`aprovar_os_painel`, `aprovar_os_confirmar`, `aprovar_os`), `templates/os/aprovar_os.html` |
| **H16** | Visualização da fila de Ordens de Serviço do dia pelo Mecânico (`aprovada` e `em_execucao`) | 2 pts | Sim | **100% Concluída** | `core/views.py` (`mecanico_os_dia`), `templates/mecanico/os_dia.html` |
| **H17** | Confirmação pelo Mecânico das peças aplicadas na OS até o limite aprovado, **sem nova baixa de estoque** | 3 pts | Sim | **100% Concluída** | `core/views.py` (`mecanico_confirmar_peca`, `confirmar_uso_peca`) |
| **H18** | Conclusão técnica da Ordem de Serviço pelo Mecânico com registro automático de data e hora (`data_conclusao`) | 2 pts | Sim | **100% Concluída** | `core/views.py` (`mecanico_concluir_os`, `concluir_os`) |

---

## 3. Regras de Negócio Críticas Garantidas na Sprint 3

1. **Baixa Atômica e Exclusiva na Aprovação da OS (`H15`):**
   - Ao aprovar uma OS com status `pendente`, o sistema bloqueia a linha da OS e todas as linhas das peças vinculadas via `select_for_update()` dentro de `transaction.atomic()`.
   - Se faltar **1 única unidade** em qualquer peça da OS, a aprovação é recusada, um alerta detalhado é exibido com o saldo atual vs. solicitado, e **nenhuma peça sofre baixa** (rollback integral).
   - A flag `estoque_baixado = True` e o timestamp `aprovada_em` garantem idempotência e impedem dupla baixa de estoque.
2. **Confirmação de Uso pelo Mecânico Sem Dupla Baixa (`H17`):**
   - Quando o mecânico registra `quantidade_utilizada` (validada no intervalo $0 \le \text{uso} \le \text{quantidade aprovada}$), o sistema atualiza `ItemPeca.quantidade_utilizada` e transiciona o status de `aprovada` para `em_execucao`, mantendo `Peca.estoque` rigorosamente inalterado.
3. **Consulta de Histórico por Placa em $< 3$s com 3 Estados Semânticos (`H05`):**
   - A busca aceita placas com ou sem máscara/hífen e minúsculas/maiúsculas (`abc-1d23`, `ABC1D23`), utilizando o índice `UNIQUE` da coluna `placa`.
   - Diferencia visualmente: **(a)** Placa não cadastrada no sistema (`CT-012`), **(b)** Veículo cadastrado sem histórico de manutenção (`CT-059`) e **(c)** Veículo com histórico completo e valores congelados (`CT-011`).

---

## 4. Resumo dos Testes da Sprint 3

As evidências detalhadas encontram-se em [sprint-3-evidencias-teste.md](sprint-3-evidencias-teste.md).

| Caso de Teste | Cenário Validado | Status |
|---|---|---|
| **CT-011** | Consulta de histórico por placa de veículo com múltiplas OSs exibe itens e totais congelados | **APROVADO** |
| **CT-012** | Consulta por placa inexistente exibe alerta específico `"Placa não cadastrada no sistema"` | **APROVADO** |
| **CT-026** | Aprovação de OS pendente com estoque suficiente baixa saldo exato e muda status para `aprovada` | **APROVADO** |
| **CT-027** | Bloqueio de aprovação quando falta estoque em uma peça (mantém OS `pendente` e saldo intacto) | **APROVADO** |
| **CT-028** | Bloqueio de aprovação por usuário sem perfil `Dono/Gerente` (`HTTP 403 Forbidden`) | **APROVADO** |
| **CT-029** | Impedimento de dupla aprovação / dupla baixa em OS já aprovada | **APROVADO** |
| **CT-030** | Listagem da fila do dia do Mecânico exibe apenas OSs `aprovada` e `em_execucao` | **APROVADO** |
| **CT-031** | Confirmação de uso de peça pelo Mecânico atualiza `quantidade_utilizada` sem alterar `Peca.estoque` | **APROVADO** |
| **CT-032** | Rejeição de `quantidade_utilizada` negativa ou superior à quantidade aprovada na OS | **APROVADO** |
| **CT-033** | Bloqueio de confirmação de peça por perfil não autorizado (`Atendente` / anônimo) | **APROVADO** |
| **CT-034** | Conclusão da OS pelo Mecânico muda status para `concluida` e preenche `data_conclusao` | **APROVADO** |
| **CT-035** | Rejeição de tentativa de concluir OS ainda `pendente` (não aprovada) | **APROVADO** |
| **CT-036** | Bloqueio de conclusão de OS por perfil não autorizado (`Atendente` / anônimo) | **APROVADO** |
| **CT-046** | Rollback transacional em OS com múltiplas peças quando apenas a última peça não tem saldo | **APROVADO** |
| **CT-059** | Consulta por placa de veículo cadastrado mas sem OSs exibe `"Veículo sem histórico de manutenção"` | **APROVADO** |
| **CT-061** | Proteção contra concorrência e dupla baixa (`select_for_update` + `estoque_baixado`) | **APROVADO** |
| **CT-062** | Invariância do estoque de peças antes, durante e após confirmação pelo mecânico e conclusão da OS | **APROVADO** |
| **CT-067** | Tempo de resposta da consulta de histórico por placa inferior a $3$ segundos | **APROVADO** |
