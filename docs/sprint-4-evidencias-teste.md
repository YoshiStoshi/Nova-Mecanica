# Evidências de Testes — Sprint 4 (E8) e Homologação Ponta a Ponta

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Sprint:** 4 (E8) — Período: 05/11/2026 a 25/11/2026  
**Escopo Testado:** Relatório de Faturamento Mensal (`H19`), Ranking de Serviços Mais Executados (`H20`), Ranking de Peças Mais Vendidas (`H21`), Não Duplicação por N:N (`CT-065`), Desempate Alfabético (`CT-066`) e Fluxo Completo Ponta a Ponta (`CT-058`).

**Comandos para Execução Reproduzível:**
```bash
python manage.py test
```

---

## 1. Matriz de Rastreabilidade e Resultados (Casos de Teste da Sprint 4 e E2E)

| Caso de Teste | História | Cenário Testado | Método / Arquivo de Teste | Resultado Obtido | Status |
|---|---|---|---|---|---|
| **CT-037** | H19 | Cálculo de faturamento mensal líquido considerando OSs com `status='concluida'` e desconto aplicado | `SprintRegressaoTests.test_relatorio_considera_concluida_com_desconto` / `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | OS concluída com subtotal R$ 100 e desconto R$ 10 contabiliza exatamente `R$ 90,00` (e no E2E, subtotal R$ 680 com 10% contabiliza `R$ 612,00`) | **PASSOU** |
| **CT-038** | H19 | Exclusão de OSs não concluídas (`pendente`, `aprovada`, `em_execucao`, `cancelada`) do faturamento mensal | `SprintRegressaoTests.test_relatorio_exclui_os_pendente` | OS com status `pendente` e total R$ 100,00 não entra no relatório (`resultados == []`) | **PASSOU** |
| **CT-039** | H19, H20, H21 | Filtro de período sem nenhuma OS concluída exibe estado vazio amigável e Ticket Médio zerado sem erro | `relatorios_dashboard` (`core/views.py`) e `templates/relatorios/dashboard.html` | Renderiza `#emptyFaturamento`, `#emptyRankingServicos`, `#emptyRankingPecas` e `ticket_medio = Decimal('0.00')` | **PASSOU** |
| **CT-040** | H20 | Ranking de Serviços Mais Executados soma quantidades de serviços em OSs concluídas em ordem decrescente | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Retorna lista ordenada por `-quantidade_executada` com receita histórica calculada por `F('quantidade') * F('preco_unitario_historico')` | **PASSOU** |
| **CT-041** | H21 | Ranking de Peças Mais Vendidas soma quantidades de peças em OSs concluídas em ordem decrescente | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Retorna lista ordenada por `-quantidade_vendida` com receita histórica congelada | **PASSOU** |
| **CT-042** | H02, H19, H20, H21 | Bloqueio de acesso aos relatórios gerenciais por usuário `Atendente`, `Mecânico` ou sem perfil | `SprintRegressaoTests.test_usuario_sem_perfil_nao_acessa_relatorio` / `Sprint3e4ViewsAndIntegrationTests.test_restricao_perfis_sprint3_e_4_ct028_033_036_042` | Retorna HTTP `403 Forbidden` tanto no Dashboard HTML quanto na API JSON | **PASSOU** |
| **CT-058** | H01 a H21 | Teste Ponta a Ponta (E2E) completo percorrendo todas as etapas do sistema | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Orçamento convertido em OS Pendente (R$ 612,00) $\rightarrow$ Aprovada pelo Dono com baixa atômica $\rightarrow$ Peças confirmadas e OS concluída pelo Mecânico $\rightarrow$ Contabilizada no Dashboard Gerencial | **PASSOU** |
| **CT-065** | H19 | Prevenção de duplicação de valores no faturamento mensal quando uma OS possui 2 peças e 2 serviços (N:N) | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Mesmo com 2 registros em `ItemPeca` e 2 registros em `ItemServico`, `total_os_concluidas == 1` e `faturamento_total_liquido == Decimal('612.00')` (sem multiplicação por 4) | **PASSOU** |
| **CT-066** | H20, H21 | Critério de desempate alfabético por `descricao` nos rankings de Serviços e Peças quando há empate na quantidade | `Sprint3e4ViewsAndIntegrationTests.test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058` | Com 1x cada serviço, ordena `["Alinhamento Técnico", "Balanceamento de Rodas"]`; com 2x cada peça, ordena `["Amortecedor Traseiro", "Bucha da Bandeja"]` | **PASSOU** |

