# Relatório Individual de Contribuição — Sprint 2 (E6)

**Aluno:** Carlos Chen  
**RA:** 2840482421030  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Banco de Dados — Integridade e Testes  
**Período:** 23/09/2026 a 14/10/2026  
**Sprint:** 2 (E6)  

---

## 1. Atividades Realizadas

- **Constraints dos itens da OS (N:N) no PostgreSQL:** no script `docs/database/01-constraints-postgresql.sql`, nas tabelas associativas de itens da OS (`core_itempeca` e `core_itemservico`):
  - `ck_core_itempeca_quantidade_positiva` e `ck_core_itemservico_quantidade_positiva`: `quantidade > 0`
  - `ck_core_itempeca_preco_historico_nao_negativo` e `ck_core_itemservico_preco_historico_nao_negativo`: `preco_unitario_historico >= 0`
- **Testes de integridade e histórico de preços** (`core/tests/test_chen_database.py`):
  - `test_item_peca_preserva_preco_historico` e `test_item_servico_preserva_preco_historico`: comprovam que alterar o preço no catálogo não muda o preço congelado do item da OS.
  - `test_quantidade_zero_reprovada_pela_validacao_django` e `test_estoque_negativo_reprovado_pela_validacao_django`: comprovam que a validação do modelo Django recusa quantidade 0 e estoque negativo.
- **Identificação e documentação de concorrência:** registro no `docs/database/README-chen.md` e no teste `ConcorrenciaPostgreSQLChecklistTestes` de que a baixa de estoque na aprovação da OS exige `transaction.atomic()` e `select_for_update` em PostgreSQL.

---

## 2. Histórias do Backlog Atendidas (E2)

| Referência (E2) | Contribuição | Status |
|---|---|---|
| **H13 / H14** — Relacionamento N:N entre OS/Peças e OS/Serviços e validações de banco | Constraints de quantidade positiva e preço histórico não negativo nos itens da OS; testes de preço congelado | Concluída |
| **H11 / H12** — Orçamento convertido em OS com desconto e histórico preservado | Testes comprovando que o preço histórico congelado não muda quando o catálogo é atualizado | Concluída |

---

## 3. Evidências

- **Arquivos:** `docs/database/01-constraints-postgresql.sql`, `core/tests/test_chen_database.py`, `docs/database/README-chen.md`
- **Comando de teste:** `python manage.py test core.tests.test_chen_database`
- **Branch / Commit:** `origin/feature/chen-sprints-1-2` (`1c7284b`)

---

## 4. Autoavaliação e Lições Aprendidas

Nesta sprint trabalhei na integridade das tabelas associativas que ligam a Ordem de Serviço às peças e aos serviços. Criei constraints de quantidade maior que zero e preço histórico não negativo, e escrevi testes mostrando que o preço congelado no item da OS não muda quando o preço no catálogo é alterado.

O que aprendi:
- O preço histórico precisa ser copiado para o item da OS no momento da inclusão. Assim, mudanças futuras no catálogo nunca recalculam o valor de ordens antigas.
- A validação do Django e as constraints do banco se complementam: o Django devolve uma mensagem amigável ao usuário e o banco de dados atua como barreira final de integridade.

