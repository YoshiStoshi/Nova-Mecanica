# Relatório Individual de Contribuição — Sprint 1 (E5)

**Aluno:** Carlos Chen  
**RA:** 2840482421030  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Banco de Dados — DDL, Constraints e Dados de Teste  
**Período:** 21/08/2026 a 22/09/2026  
**Sprint:** 1 (E5)  

---

## 1. Atividades Realizadas

- **Constraints de integridade no PostgreSQL para o catálogo (H06, H07):** script `docs/database/01-constraints-postgresql.sql`, que adiciona CHECKs apenas se ainda não existirem (idempotente):
  - `ck_core_peca_estoque_nao_negativo` — `estoque >= 0`
  - `ck_core_peca_preco_nao_negativo` — `preco >= 0`
  - `ck_core_servico_preco_nao_negativo` — `preco >= 0`
- **Dados sintéticos de homologação:** `docs/database/02-seeds-homologacao.sql` — 1 cliente, 1 veículo, 1 peça e 1 serviço de teste, inseridos com `WHERE NOT EXISTS` (não duplicam em nova execução) e sem assumir IDs fixos.
- **Documentação do banco:** `docs/database/README-chen.md` com a ordem recomendada (`migrate` → conferir dados → constraints → seeds → testes) e avisos para não rodar seeds em produção.

---

## 2. Histórias do Backlog Atendidas (E2)

| Item do Backlog (E2) | Critério de Aceite Relacionado | Contribuição | Status |
|---|---|---|---|
| **H06 / H07** — Dono/Gerente cadastra peças e serviços | "Não deixar colocar estoque ou preço negativo" | Constraints CHECK `estoque >= 0` e `preco >= 0` no PostgreSQL | Concluída |

Observação: o critério "impedir apagar peça vinculada a uma OS" (H09) é tratado pela regra de exclusão protegida (`on_delete=models.PROTECT`) nos modelos do Django e nas views de catálogo.

---

## 3. Evidências

- **Arquivos:** `docs/database/01-constraints-postgresql.sql`, `docs/database/02-seeds-homologacao.sql`, `docs/database/README-chen.md`
- **Branch / Commit:** `origin/feature/chen-sprints-1-2` (`1c7284b`)

---

## 4. Autoavaliação e Lições Aprendidas

O que aprendi:
- As migrations do Django são a fonte de verdade do esquema, enquanto os scripts SQL atuam como camada complementar de garantia relacional no PostgreSQL.
- Antes de aplicar uma constraint em um banco existente, é preciso conferir se não há registros que a violem.
- Escrever scripts idempotentes (`IF NOT EXISTS` e `WHERE NOT EXISTS`) evita falhas ou duplicações em reexecuções.

