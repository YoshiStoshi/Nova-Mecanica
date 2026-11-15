# Relatório Individual de Contribuição — Sprint 4 (E8)

**Aluno:** Felipe Delchiaro Malzoni  
**RA:** 2840482421025  
**Projeto:** Nova Mecânica  
**Sprint:** 4 (E8) · **Período:** 05/11/2026 a 25/11/2026  
**Papel nesta sprint:** Desenvolvedor Backend / Relatório de Faturamento Mensal e Testes de Regressão  

---

## 1. O que fiz

| Item | Arquivo | Status |
|---|---|---|
| Restringi o relatório gerencial ao perfil `Dono/Gerente` via `@exigir_perfil(PERFIL_DONO)` (`H19`). | `core/views.py` | Concluído |
| Implementei a view analítica `faturamento_mensal` filtrando estritamente OSs com `status="concluida"` e agrupando por `TruncMonth("data_conclusao")` (`H19`). | `core/views.py` | Concluído |
| Garanti a agregação financeira (`Sum("total")`, `Sum("valor_desconto")`, `Count("id", distinct=True)`) diretamente sobre `OrdemServico`, evitando duplicação por joins N:N. | `core/views.py` | Concluído |
| Implementei a bateria `SprintRegressaoTests` validando exclusão de OS pendente no faturamento, cálculo líquido com desconto em OS concluída, bloqueio HTTP 403 para usuário sem perfil e proteção de peça vinculada. | `core/tests/test_sprints_regressao.py` | Concluído |
| Registrei a rota de faturamento mensal diretamente em `core/urls.py`. | `core/urls.py` | Concluído |

- **Evidências no Repositório:** Commit `4a8fb8a` (`origin/Features/Felipe`), integrado na branch `main` via `PR #5` (`890c859`).

---

## 2. Rituais que participei

- [x] Dailies/weeklies — Alinhamento das queries agregadas e filtros de período (`inicio` e `fim`)
- [x] Sprint Review — Validação do endpoint JSON de faturamento mensal e testes de regressão
- [x] Retrospectiva — Fechamento técnico das 4 sprints

---

## 3. Dificuldades e o que aprendi

Em consultas SQL que envolvem Ordens de Serviço com múltiplas peças (`ItemPeca`) e múltiplos serviços (`ItemServico`), fazer `SUM` após um `JOIN` com as tabelas associativas multiplica indevidamente o valor da OS. Como o projeto já persiste `total` e `valor_desconto` consolidados na tabela `OrdemServico`, realizei o agrupamento (`TruncMonth("data_conclusao")`) diretamente sobre `OrdemServico.objects.filter(status="concluida")`, garantindo exatidão contábil e alta performance.

---

## 4. Status de Integração no Projeto

View analítica consolidada em `core/views.py`, rota integrada em `core/urls.py` e suíte de regressão estruturada em `core/tests/test_sprints_regressao.py`.
