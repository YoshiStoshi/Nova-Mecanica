# Relatório Individual de Contribuição — Sprint 2 (E6)

**Aluno:** João Gabriel Cardoso Martarello<br>
**RA:** 2840482421028<br>
**Projeto:** Nova Mecânica<br>
**Papel no Semestre:** Desenvolvedor Backend / UI Bootstrap<br>
**Período:** 23/09/2026 a 14/10/2026<br>
**Sprint:** 2 (E6)

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 2, atuei no cálculo financeiro do orçamento e nos serviços transacionais responsáveis pela inclusão e remoção de peças e serviços na Ordem de Serviço:

- **Cálculo Monetário e Desconto (`H11`):**
  - Implementação da função `calcular_totais` em `core/calculos.py` usando `Decimal`, sem operações financeiras com `float`.
  - Validação do desconto no intervalo de 0% a 100%, rejeitando valores inválidos, infinitos ou fora dos limites.
  - Cálculo do subtotal, valor do desconto e total líquido com arredondamento `ROUND_HALF_UP` em duas casas decimais.
  - Rejeição de quantidades não inteiras ou menores que 1 e de preços negativos ou com mais de duas casas decimais.

- **Itens de Peça na OS (`H13`):**
  - Implementação de `incluir_item` e `remover_item` em `core/services.py` com `transaction.atomic`.
  - Cópia do preço atual da peça para `preco_unitario_historico`, preservando o valor da OS após futuras alterações no catálogo.
  - Bloqueio de peças duplicadas na mesma OS e recálculo automático dos totais após inclusão ou remoção.
  - Garantia de que a inclusão da peça na OS pendente não realiza baixa de estoque.

- **Itens de Serviço na OS (`H14`):**
  - Reutilização do serviço transacional para associar serviços com quantidade e preço histórico.
  - Implementação dos controllers `ordem_item_adicionar` e `ordem_item_remover`, com verificação das permissões correspondentes.
  - Preservação da independência entre os itens de diferentes Ordens de Serviço.

- **Alteração de Desconto e Bloqueio Pós-Aprovação:**
  - Implementação de `alterar_desconto` e `recalcular_ordem` para manter subtotal, desconto e total sincronizados.
  - Uso de `select_for_update` em `ordem_pendente_bloqueada` para serializar alterações na mesma OS.
  - Bloqueio de inclusão, remoção ou alteração de desconto quando a OS não está mais no status `pendente`.

- **Testes Automatizados:**
  - Cobertura dos limites de desconto, arredondamento monetário e entradas inválidas.
  - Testes de inclusão e remoção de itens, duplicidade, preços históricos e rollback quando o recálculo falha.
  - Verificação de que dados enviados pelo navegador não substituem o preço oficial do catálogo.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H11** (Desconto e Totalização) | Cálculo decimal, validação de limites e arredondamento monetário | Concluída |
| **H13** (Peças na OS) | Inclusão/remoção transacional com quantidade e preço histórico | Concluída |
| **H14** (Serviços na OS) | Inclusão/remoção transacional com quantidade e preço histórico | Concluída |

---

## 3. Evidências Técnicas

- `core/calculos.py` — Função `calcular_totais`.
- `core/services.py` — Serviços `incluir_item`, `remover_item`, `alterar_desconto` e `recalcular_ordem`.
- `core/forms.py` — `DescontoForm`, `ItemPecaForm` e `ItemServicoForm`.
- `core/views.py` — Controllers de desconto e manipulação dos itens da OS.
- `core/tests/test_cadastros_e_ordens.py` — Testes unitários e de integração do cálculo e das operações da OS.
- **Commit:** `82aa9e5` — implementação de cadastros, cálculos e validações.
- **Pull Request:** `PR #2` — integração da branch `joao-sprint1e2` na `main`.
- **Comando de validação:** `python manage.py test core.tests.test_cadastros_e_ordens`

---

## 4. Autoavaliação e Lições Aprendidas

Separar o motor financeiro em `calculos.py` e as operações transacionais em `services.py` tornou as regras mais fáceis de testar e reutilizar. O uso de `Decimal` evitou divergências de centavos, enquanto o congelamento do preço histórico garantiu que mudanças futuras no catálogo não alterassem ordens existentes. As transações também asseguraram que uma falha no recálculo desfizesse toda a operação, sem deixar itens ou totais inconsistentes.
