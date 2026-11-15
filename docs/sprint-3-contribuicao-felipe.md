# Relatório Individual de Contribuição — Sprint 3 (E7)

**Aluno:** Felipe Delchiaro Malzoni  
**RA:** 2840482421025  
**Projeto:** Nova Mecânica  
**Sprint:** 3 (E7) · **Período:** 15/10/2026 a 04/11/2026  
**Papel nesta sprint:** Desenvolvedor Backend / Aprovação Atômica de OS, Baixa de Estoque e Fluxo do Mecânico  

---

## 1. O que fiz

| Item | Arquivo | Status |
|---|---|---|
| Implementei `aprovar_os` exclusivo para `Dono/Gerente` com `select_for_update()` na OS e nas peças vinculadas (`H15`). | `core/views.py` | Concluído |
| Implementei verificação atômica de saldo de todas as peças da OS antes da baixa, disparando rollback completo caso falte qualquer item (`H15`). | `core/views.py` | Concluído |
| Implementei trava `estoque_baixado` e timestamp `aprovada_em` para impedir baixa duplicada de estoque. | `core/views.py` / `core/models.py` | Concluído |
| Implementei `confirmar_uso_peca` exclusivo para o perfil `Mecânico`, registrando `quantidade_utilizada` e transicionando a OS para `em_execucao` **sem realizar nova baixa no estoque** (`H17`). | `core/views.py` | Concluído |
| Implementei `concluir_os` exclusivo para o perfil `Mecânico`, encerrando a OS em execução e gravando `data_conclusao = timezone.now()` (`H18`). | `core/views.py` | Concluído |
| Consolidei as rotas de aprovação e execução em `core/urls.py` e as migrations (`0002_ordemservico_campos_sprint3_4.py`). | `core/views.py` / `core/urls.py` | Concluído |

- **Evidências no Repositório:** Commit `4a8fb8a` (`origin/Features/Felipe`), integrado na branch `main` via `PR #5` (`890c859`).

---

## 2. Rituais que participei

- [x] Dailies/weeklies — Definição dos campos `estoque_baixado`, `aprovada_em`, `data_conclusao` e `quantidade_utilizada`
- [x] Sprint Review — Validação da baixa atômica de estoque na aprovação e confirmação pelo mecânico
- [x] Retrospectiva — Preparação dos dados de conclusão para os relatórios gerenciais da Sprint 4

---

## 3. Dificuldades e o que aprendi

A regra mais crítica do projeto determina que a baixa de estoque ocorre **exclusivamente na aprovação da OS pelo Dono/Gerente (H15)** e nunca na confirmação de uso pelo mecânico (H17). Para evitar deadlocks e condições de corrida no banco, ordenei a leitura dos itens por `peca_id` e apliquei `select_for_update()` tanto na `OrdemServico` quanto no conjunto de `Peca`. Se qualquer peça tiver saldo menor que o solicitado, uma `ValidationError` é levantada dentro de `@transaction.atomic`, revertendo qualquer alteração e mantendo a OS como `pendente`.

---

## 4. Status de Integração no Projeto

Campos adicionados em `core/models.py` (migration `0002_ordemservico_campos_sprint3_4.py`), views consolidadas em `core/views.py` e rotas integradas diretamente em `core/urls.py`.
