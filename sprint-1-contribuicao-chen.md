# Relatório Individual de Contribuição — Sprint 1 (E5)

**Aluno:** Carlos Chen · **RA:** 2840482421030 
**Projeto:** Nova Mecânica · **Papel:** Banco de dados — DDL, constraints e dados de teste
**Sprint:** 1 (E5) · **Período:** 21/08/2026 a 22/09/2026 

> Rascunho montado a partir dos arquivos do repositório. Confirme com a sua memória/histórico do Git o que foi feito nesta sprint e em qual sprint cada item entrou; ajuste o que não bater.

## 1. Atividades Realizadas

- **Constraints de integridade no PostgreSQL para o catálogo (H06, H07):** script `docs/database/01-constraints-postgresql.sql`, que adiciona CHECKs apenas se ainda não existirem (idempotente):
  - `ck_core_peca_estoque_nao_negativo` — `estoque >= 0`
  - `ck_core_peca_preco_nao_negativo` — `preco >= 0`
  - `ck_core_servico_preco_nao_negativo` — `preco >= 0`
- **Dados sintéticos de homologação:** `docs/database/02-seeds-homologacao.sql` — 1 cliente, 1 veículo, 1 peça e 1 serviço de teste, inseridos com `WHERE NOT EXISTS` (não duplicam em nova execução) e sem assumir IDs fixos.
- **Documentação do banco:** `docs/database/README-chen.md` com a ordem recomendada (migrate → conferir dados → constraints → seeds → testes) e avisos para não rodar seeds em produção.

## 2. Histórias do Backlog Atendidas (E2)

Numeração conforme o Backlog Priorizado do E2 (Sprint 1 = itens 1 a 3):

| Item do backlog (E2) | Critério de aceite relacionado | Contribuição | Status |
|---|---|---|---|
| **#3** — Dono/Gerente cadastra peças e serviços | "Não deixar colocar estoque negativo" | CHECK `estoque >= 0` no PostgreSQL (e preços não negativos) 

Observação: o outro critério do item #3 ("impedir apagar peça vinculada a uma OS") é tratado pela regra de exclusão protegida do Django e não consta nos scripts SQL desta contribuição, por isso não foi listado como contribuição sua.

## 3. Evidências

- Arquivos: `docs/database/01-constraints-postgresql.sql`, `docs/database/02-seeds-homologacao.sql`, `docs/database/README-chen.md`
- Commits/PRs: --
- Resultado da execução dos scripts no PostgreSQL da equipe: não executados nesta sprint.

## 4. Autoavaliação e Lições Aprendidas


O que aprendi:
- As migrations do Django são a fonte de verdade do esquema. Meus scripts SQL são complementares e precisam ser revisados antes de serem usados fora do ambiente de desenvolvimento.
- Antes de aplicar uma constraint, é preciso conferir se já existem dados que a violam, senão o comando falha.
- Escrevi os scripts de forma que possam ser executados mais de uma vez sem duplicar nada (`IF NOT EXISTS` e `WHERE NOT EXISTS`).

O que faltou: não executei os scripts no PostgreSQL da equipe durante a sprint, então não tenho evidência de execução para anexar. Na próxima sprint pretendo rodar os scripts e registrar o resultado real antes da entrega.