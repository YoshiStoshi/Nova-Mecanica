# Relatório Individual de Contribuição — Sprint 2 (E6)

**Aluno:** Felipe Delchiaro Malzoni  
**RA:** 2840482421025  
**Projeto:** Nova Mecânica  
**Sprint:** 2 (E6) · **Período:** 23/09/2026 a 14/10/2026  
**Papel nesta sprint:** Desenvolvedor Backend / Estoque, Orçamento e Conversão em OS  

---

## 1. O que fiz

| Item | Arquivo | Status |
|---|---|---|
| Unifiquei o decorator `@exigir_perfil` restringindo orçamentos a `Dono/Gerente` e `Atendente` e estoque a `Dono/Gerente`. | `core/views.py` | Concluído |
| Implementei `converter_orcamento_em_os` criando a OS com status `pendente`, congelando `preco_unitario_historico` de peças e serviços sem baixar estoque (`H12`, `H13`, `H14`). | `core/views.py` | Concluído |
| Implementei validação de desconto percentual entre `0%` e `100%` com `Decimal` e recálculo via `recalcular_ordem` (`H11`). | `core/views.py` | Concluído |
| Implementei `ajustar_estoque_api` com `select_for_update()` e `transaction.atomic()` para operações `adicionar`, `remover` e `definir`, bloqueando saldo negativo (`H08`). | `core/views.py` | Concluído |
| Implementei `excluir_peca_protegida_api` com lock de linha, impedindo exclusão quando `peca.itens_os.exists()` (`H09`). | `core/views.py` | Concluído |
| Registrei as rotas de conversão de orçamento e APIs de estoque diretamente em `core/urls.py`. | `core/urls.py` | Concluído |

- **Evidências no Repositório:** Commit `4a8fb8a` (`origin/Features/Felipe`), integrado na branch `main` via `PR #5` (`890c859`).

---

## 2. Rituais que participei

- [x] Dailies/weeklies — Alinhamento do payload de conversão de orçamento (`pecas_id[]`, `pecas_qtd[]`, `servicos_id[]`, `servicos_qtd[]`)
- [x] Sprint Review — Homologação das histórias H08 a H14
- [x] Retrospectiva — Planejamento das migrations e locks para aprovação de OS na Sprint 3

---

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| `PR #2` / `PR #3` | João Gabriel / Rodrigo | Alinhamento da chamada a `recalcular_ordem` em `core/services.py` e dos campos enviados por `orcamento.js`. |

---

## 4. Dificuldades e o que aprendi

Na conversão do orçamento em Ordem de Serviço, foi fundamental garantir que toda a gravação da OS e de seus múltiplos itens (`ItemPeca` e `ItemServico`) ocorresse dentro de um único bloco `transaction.atomic()`. Caso qualquer item tenha quantidade inválida, não exista ou viole a constraint de unicidade (`IntegrityError`), toda a operação sofre rollback. Além disso, no ajuste de estoque (`H08`), utilizei `Peca.objects.select_for_update()` para evitar condições de corrida e impedir que o saldo fique negativo.

---

## 5. Status de Integração no Projeto

Todas as views e endpoints da Sprint 2 (originalmente entregues em `sprint2_backend.py`) foram consolidados em `core/views.py` e roteados diretamente em `core/urls.py`.
