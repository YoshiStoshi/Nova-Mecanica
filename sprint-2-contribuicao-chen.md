# Relatório Individual de Contribuição — Sprint 2 (E6)

**Aluno:** Carlos Chen
**RA:** 2840482421030
**Projeto:** Nova Mecânica
**Papel:** Banco de dados — integridade e testes
**Sprint:** 2 (E6)
**Período:** 23/09/2026 a 14/10/2026

---

## 1. Atividades Realizadas

- **Constraints dos itens da OS (N:N) no PostgreSQL:** no script `docs/database/01-constraints-postgresql.sql`, nas tabelas de itens da OS (nesta fase chamadas `core_itempeca` e `core_itemservico`):
  - `ck_core_itempeca_quantidade_positiva` e `ck_core_itemservico_quantidade_positiva`: `quantidade > 0`
  - `ck_core_itempeca_preco_historico_nao_negativo` e `ck_core_itemservico_preco_historico_nao_negativo`: `preco_unitario_historico >= 0`
- **Testes de integridade e histórico de preços** (`core/tests/test_chen_database.py`, 4 testes):
  - `test_item_peca_preserva_preco_historico` e `test_item_servico_preserva_preco_historico`: alterar o preço no catálogo não muda o preço congelado do item da OS.
  - `test_quantidade_zero_reprovada_pela_validacao_django` e `test_estoque_negativo_reprovado_pela_validacao_django`: a validação do Django recusa quantidade 0 e estoque negativo.
- **Identificação de risco de concorrência:** registrei no `README-chen.md` e no teste `ConcorrenciaPostgreSQLChecklistTestes` que a baixa de estoque exigirá `transaction.atomic()` e `select_for_update`, e que isso só pode ser validado em PostgreSQL. Nesta fase o teste apenas verifica qual banco está em uso e é pulado fora do PostgreSQL.

---

## 2. Histórias do Backlog Atendidas (E2)

| Referência (E2) | Contribuição | Status |
|---|---|---|
| Critério de pronto do MVP: N:N entre OS/Peças e OS/Serviços, e validações de banco ativas | Constraints de quantidade e preço histórico nos itens da OS (script SQL); testes de preço congelado | Parcial: scripts escritos, ainda não executados no banco da equipe |
| Item #4: orçamento convertido em OS com desconto | Testes de que o preço histórico não muda com o catálogo, que é a base do total da OS | Parcial: apoio de integridade; o cálculo do desconto é de outro integrante |
| Item #5: aprovar OS com baixa automática de estoque | Não entregue nesta contribuição: apenas o risco de concorrência foi identificado | Pendente |

---

## 3. Evidências

- Arquivos: `docs/database/01-constraints-postgresql.sql`, `core/tests/test_chen_database.py`, `docs/database/README-chen.md`
- Comando de teste: `python manage.py test core.tests.test_chen_database`
- Resultado da execução no PostgreSQL da equipe: não executado nesta sprint.
- Commits/PRs: --

---

## 4. Pendências reconhecidas nesta sprint

- Teste de concorrência da baixa de estoque não implementado, pois depende da regra de aprovação da OS.
- Seeds para teste de carga não criados.
- Scripts SQL e testes não executados no PostgreSQL da equipe.

---

## 5. Autoavaliação e Lições Aprendidas

Nesta sprint trabalhei na integridade das tabelas que ligam a Ordem de Serviço às peças e aos serviços. Criei constraints de quantidade maior que zero e preço histórico não negativo, e escrevi testes mostrando que o preço congelado no item da OS não muda quando o preço no catálogo é alterado.

O que aprendi:
- O preço histórico precisa ser copiado para o item da OS no momento da inclusão. Assim, mudanças no catálogo não alteram o valor de ordens antigas.
- A validação do Django e as constraints do banco se complementam: o Django devolve uma mensagem amigável, e o banco é a última barreira.
- A baixa automática de estoque exige transação e bloqueio da linha (`transaction.atomic()` e `select_for_update`), e isso só pode ser provado em PostgreSQL.

O que não foi entregue: o teste real de concorrência da baixa de estoque ficou pendente, porque a baixa na aprovação da OS ainda não estava implementada. Também não criei seeds para teste de carga, e não executei os scripts no PostgreSQL da equipe. Na próxima sprint pretendo implementar o teste de concorrência junto com o responsável pela regra de negócio e rodar tudo em PostgreSQL, registrando a saída real.