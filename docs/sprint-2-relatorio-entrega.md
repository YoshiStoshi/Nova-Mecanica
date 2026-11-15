# Relatório de Entrega da Sprint 2 (E6) — Documento Capa

**Projeto:** Nova Mecânica — Sistema de Gestão para Oficina Mecânica  
**Disciplina:** Laboratório de Software 3 (Laboratório de Engenharia de Software) — Trilha B  
**Instituição:** FATEC Ribeirão Preto — Curso de Análise e Desenvolvimento de Sistemas (ADS)  
**Sprint:** 2 (E6) — Gestão de Estoque, Orçamento Dinâmico, Relacionamento N:N e Conversão em OS Pendente  
**Período da Sprint:** 23/09/2026 a 14/10/2026  
**URL de Produção / Homologação (Render):** `https://nova-mecanica.onrender.com`  
**Repositório Oficial:** `https://github.com/YoshiStoshi/Nova-Mecanica`  

---

## 1. Identificação da Equipe Oficial

| Integrante | RA | Papel Principal na Sprint 2 | Relatório Individual |
|---|---|---|---|
| **Rodrigo de Azevedo Junior** | `2840482421044` | Interface Dinâmica de Orçamento (`orcamento_form.html`), Cálculo em Tempo Real (`orcamento.js`), Modais de Estoque/Exclusão e Conversão em OS | [sprint-2-contribuicao-rodrigo.md](sprint-2-contribuicao-rodrigo.md) |
| **João Gabriel Cardoso Martarello** | `2840482421028` | Motor de Cálculo Decimal (`calculos.py`), Serviços Transacionais N:N (`services.py`) e Testes de Integração de OS | [joao-sprint1e2.md](joao-sprint1e2.md) |
| **Felipe Delchiaro Malzoni** | `2840482421025` | Endpoints de Conversão de Orçamento, Ajuste de Estoque com `select_for_update` e Exclusão Protegida (`core/views.py`) | [sprint-2-contribuicao-felipe.md](sprint-2-contribuicao-felipe.md) |
| **Carlos Chen** | `2840482421030` | Modelagem Associativa N:N (`ItemPeca`, `ItemServico`), Constraints PostgreSQL dos Itens da OS e Testes de Preço Histórico Congelado (`test_chen_database.py`) | [sprint-2-contribuicao-chen.md](sprint-2-contribuicao-chen.md) |

---

## 2. Escopo da Sprint 2: Planejado vs. Entregue (H08 a H14)

| ID | História de Usuário (Backlog E2) | Prioridade | Planejado | Entregue | Evidência Principal no Repositório |
|---|---|---|---|---|---|
| **H08** | Ajuste manual de saldo de estoque de peças pelo Dono/Gerente com bloqueio de saldo negativo | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`peca_ajustar_estoque`, `ajustar_estoque_api`), `templates/catalogo/pecas_list_form.html` |
| **H09** | Exclusão segura de peças do catálogo bloqueando itens vinculados a Ordens de Serviço | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`peca_excluir`, `excluir_peca_protegida_api`), `core/models.py` (`on_delete=models.PROTECT`) |
| **H10** | Montagem dinâmica de orçamento selecionando cliente, veículo, peças e serviços em tela única | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`orcamento_novo`), `templates/orcamentos/orcamento_form.html`, `static/js/orcamento.js` |
| **H11** | Aplicação de desconto percentual ($0\%$ a $100\%$) e cálculo automático do valor líquido em tempo real e no backend | Alta (MVP) | Sim | **100% Concluída** | `core/calculos.py` (`calcular_totais`), `static/js/orcamento.js`, `core/services.py` (`alterar_desconto`) |
| **H12** | Conversão de orçamento em Ordem de Serviço com status inicial `Pendente` sem baixar estoque prematuramente | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`orcamento_converter`), `templates/orcamentos/orcamento_form.html` (`#modalConfirmarConversao`) |
| **H13** | Associação N:N de múltiplas peças na OS com quantidade ($\ge 1$) e congelamento do preço unitário histórico | Alta (MVP) | Sim | **100% Concluída** | `core/models.py` (`ItemPeca`), `core/services.py` (`incluir_item`, `remover_item`), `templates/core/ordem_detalhe.html` |
| **H14** | Associação N:N de múltiplos serviços na OS com quantidade ($\ge 1$) e congelamento do preço unitário histórico | Alta (MVP) | Sim | **100% Concluída** | `core/models.py` (`ItemServico`), `core/services.py` (`incluir_item`, `remover_item`), `templates/core/ordem_detalhe.html` |

---

## 3. Cumprimento das Regras de Negócio Críticas na Sprint 2

1. **Histórico Financeiro Congelado (H13, H14):**
   - No momento da conversão do orçamento (`orcamento_converter`) ou da adição de item em uma OS pendente (`incluir_item`), o valor atual de `peca.preco` ou `servico.preco` é copiado para `preco_unitario_historico` nas tabelas associativas `core_itempeca` e `core_itemservico`.
   - Alterações posteriores nos preços do catálogo (`H06`, `H07`) **nunca** alteram o subtotal ou total das Ordens de Serviço já registradas (comprovado pelo caso de teste `CT-054`).
2. **Preservação do Estoque no Orçamento e na OS Pendente (H12, H15):**
   - A inclusão de peças no orçamento ou na OS com status `pendente` **não reduz** o saldo de `Peca.estoque`. A baixa atômica ocorre exclusivamente na aprovação da OS pelo Dono/Gerente (`H15`).
3. **Precisão Matemática e Validação Estrita de Desconto (H11):**
   - O cálculo utiliza `Decimal` com arredondamento `ROUND_HALF_UP` para 2 casas decimais em `core/calculos.py`.
   - Descontos fora do intervalo $[0\%, 100\%]$, strings não numéricas, `NaN`, `Infinity` ou com mais de 2 casas decimais são rejeitados tanto no frontend (`orcamento.js`) quanto no backend (`calcular_totais` e `DescontoForm`).
4. **Integridade Relacional e Bloqueio de Edição Fora de Status Pendente:**
   - Constraint `UniqueConstraint(fields=['ordem', 'peca'])` e `UniqueConstraint(fields=['ordem', 'servico'])` impedem linhas duplicadas do mesmo item na mesma OS.
   - Qualquer tentativa de adicionar/remover itens ou alterar desconto em uma OS com status diferente de `pendente` (`aprovada`, `em_execucao`, `concluida`) é bloqueada no servidor com status HTTP `400`.

---

## 4. Resumo dos Testes Automatizados da Sprint 2

As evidências completas encontram-se em [sprint-2-evidencias-teste.md](sprint-2-evidencias-teste.md).

| Caso de Teste / Regra | Descrição Resumida | Status |
|---|---|---|
| **H08 (Estoque Positivo/Fixo)** | Ajuste de estoque (`adicionar` e `definir`) atualiza saldo corretamente | **APROVADO** |
| **H08 (Bloqueio Saldo Negativo)** | Tentativa de remover quantidade maior que o saldo atual é rejeitada no front e no back | **APROVADO** |
| **H09 (Exclusão Protegida)** | Peça vinculada a OS não pode ser excluída; peça sem vínculo é excluída com sucesso | **APROVADO** |
| **CT-019 / H13 / H14** | Inclusão e remoção de múltiplas peças e serviços recalcula subtotal e total sem baixar estoque | **APROVADO** |
| **CT-020 / CT-021 / CT-064** | Cálculo de desconto nos limites ($0\%$, $10\%$, $100\%$) e arredondamento `ROUND_HALF_UP` | **APROVADO** |
| **CT-022** | Rejeição de descontos inválidos ($-1\%$, $101\%$, `NaN`, `abc`) preservando total anterior | **APROVADO** |
| **CT-050 / CT-051** | Independência de itens N:N entre diferentes Ordens de Serviço | **APROVADO** |
| **CT-054** | Alteração de preço no catálogo de Peças/Serviços não altera `preco_unitario_historico` nem total da OS | **APROVADO** |
| **CT-063 / CT-068** | Rejeição de quantidades inválidas ($0$, $-1$, decimal), itens inexistentes ou duplicados na mesma OS | **APROVADO** |
| **H12 (Conversão em OS)** | Conversão de orçamento cria OS com status `pendente`, congela preços e calcula desconto/total líquido | **APROVADO** |

---

## 5. Artefatos da Entrega na Pasta `docs/`

- [sprint-2-relatorio-entrega.md](sprint-2-relatorio-entrega.md) — Documento Capa da Sprint 2 (este arquivo)
- [sprint-2-retrospectiva.md](sprint-2-retrospectiva.md) — Ata Oficial de Retrospectiva da Sprint 2
- [sprint-2-evidencias-teste.md](sprint-2-evidencias-teste.md) — Caderno de Evidências de Testes da Sprint 2
- [sprint-2-contribuicao-rodrigo.md](sprint-2-contribuicao-rodrigo.md) — Relatório Individual (Rodrigo de Azevedo Junior)
- [joao-sprint1e2.md](joao-sprint1e2.md) — Relatório Individual (João Gabriel Cardoso Martarello)
- [sprint-2-contribuicao-felipe.md](sprint-2-contribuicao-felipe.md) — Relatório Individual (Felipe Delchiaro Malzoni)
- [sprint-2-contribuicao-chen.md](sprint-2-contribuicao-chen.md) — Relatório Individual (Carlos Chen)

