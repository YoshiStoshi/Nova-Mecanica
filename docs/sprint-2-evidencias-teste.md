# Evidências de Testes — Sprint 2 (E6)

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Sprint:** 2 (E6) — Período: 23/09/2026 a 14/10/2026  
**Escopo Testado:** Gestão de Estoque (`H08`), Exclusão Protegida (`H09`), Orçamento Dinâmico (`H10`), Cálculo de Desconto e Limites (`H11`), Conversão em OS Pendente (`H12`) e Relacionamento N:N com Preço Histórico Congelado (`H13`, `H14`).

**Comando para Execução da Suíte Completa:**
```bash
python manage.py test
```

---

## 1. Matriz de Rastreabilidade e Resultados (Sprint 2)

| Caso de Teste / Requisito | História | Cenário de Teste | Método de Teste Automatizado | Resultado Obtido | Status |
|---|---|---|---|---|---|
| **Ajuste de Estoque (+ / =)** | H08 | Dono/Gerente adiciona unidades ao estoque (+5) e define novo saldo fixo (=20) | `Sprint1e2Tests.test_ajuste_estoque_adicionar_e_definir_h08` | Estoque passa de `10` para `15` e depois para `20` com mensagem de sucesso | **PASSOU** |
| **Bloqueio de Saldo Negativo** | H08, CT-048 | Tentativa de subtrair 15 unidades de uma peça com saldo 10 | `Sprint1e2Tests.test_ajuste_estoque_rejeita_saldo_negativo_h08` | Operação recusada, saldo permanece intacto em `10` | **PASSOU** |
| **Exclusão de Peça Vinculada** | H09 | Tentativa de excluir peça que já possui registro em `ItemPeca` de uma OS | `Sprint1e2Tests.test_exclusao_peca_protegida_com_vinculo_os_h09` | Exclusão bloqueada, `Peca.objects.filter(pk=...).exists()` permanece `True` | **PASSOU** |
| **Exclusão de Peça Sem Vínculo** | H09 | Exclusão de peça recém-cadastrada sem vínculo com nenhuma OS | `Sprint1e2Tests.test_exclusao_peca_sem_vinculo_sucesso_h09` | Peça removida do catálogo com sucesso | **PASSOU** |
| **Carregamento do Orçamento Dinâmico** | H10 | Atendente acessa `/orcamentos/novo/` com catálogos de clientes, veículos, peças e serviços serializados | `Sprint1e2Tests.test_tela_orcamento_novo_carrega_com_sucesso_h10` | HTTP `200 OK` contendo JSON de veículos, peças e serviços e estrutura dinâmica | **PASSOU** |
| **Rejeição de Orçamento Vazio** | H10 | Submissão de orçamento sem nenhuma peça e sem nenhum serviço | `Sprint1e2Tests.test_conversao_orcamento_rejeita_sem_itens_h10` | Redireciona para `/orcamentos/novo/` com erro e `OrdemServico.objects.count() == 0` | **PASSOU** |
| **Conversão de Orçamento em OS Pendente** | H11, H12, H13, H14 | Conversão de orçamento com 2x Peça (R$ 120,00) + 1x Serviço (R$ 150,00) e desconto de 10% | `Sprint1e2Tests.test_conversao_orcamento_em_os_sucesso_h11_h12` | Cria OS com status `pendente`, subtotal `R$ 390,00`, desconto `R$ 39,00`, total `R$ 351,00` e congela preços históricos sem baixar estoque | **PASSOU** |
| **Limites de Desconto (0%, 10%, 100%) e Arredondamento** | H11, CT-020, CT-021, CT-064 | Cálculo de subtotal, desconto e total líquido em casos de borda (`0%`, `100%`, dízimas como `1.01` com `10%`, `0.05` com `10%`) | `CalculoTests.test_desconto_limites_e_arredondamento_ct020_021_064` | Arredondamento `ROUND_HALF_UP` exato em 2 casas decimais; com 100% de desconto o total líquido é `0.00` | **PASSOU** |
| **Rejeição de Descontos Inválidos** | H11, CT-022 | Descontos `-1%`, `101%`, `120%`, `NaN`, `Infinity`, `abc`, `0.001` | `CalculoTests.test_descontos_invalidos_ct022` / `Sprint1e2Tests.test_conversao_orcamento_rejeita_desconto_invalido_h11` / `ControllersCadastrosEOrdensTests.test_desconto_invalido_preserva_total_e_formulario_ct022` | `ValidationError` / HTTP `400`, preservando o total anterior da OS (`R$ 60,00`) | **PASSOU** |
| **Inclusão/Remoção N:N na OS e Estoque Intacto** | H13, H14, CT-019 | Adição de peça (2x R$ 30) e serviço (1x R$ 80), aplicação de 10% de desconto e posterior remoção dos itens | `ControllersCadastrosEOrdensTests.test_incluir_remover_e_desconto_persistido_ct019_020` | Total vai a `R$ 126,00`, volta a `R$ 0,00` após remoção, e `peca.estoque` permanece `5` (sem baixa prematura) | **PASSOU** |
| **Independência N:N entre Ordens Distintas** | H13, H14, CT-050, CT-051 | Mesma peça e mesmo serviço inseridos em duas OSs diferentes; remoção em uma OS não afeta a outra | `ControllersCadastrosEOrdensTests.test_itens_independentes_entre_ordens_ct050_051` | Segunda OS preserva suas quantidades (`3`) e seu total (`R$ 330,00`) | **PASSOU** |
| **Imutabilidade do Preço Histórico** | H13, H14, CT-054 | Alteração do preço da peça (de R$ 30 para R$ 35) e do serviço (de R$ 80 para R$ 90) no catálogo após inclusão na OS | `ControllersCadastrosEOrdensTests.test_historico_de_preco_e_estoque_preservados_ct054` / `IntegridadeCatalogoEHistoricoTests.test_item_peca_preserva_preco_historico` | `preco_unitario_historico` permanece `30.00` e `80.00`; total da OS permanece `140.00` | **PASSOU** |
| **Rejeição de Quantidades Inválidas e Duplicatas** | H13, H14, CT-063, CT-068 | Quantidade `0`, `-1`, `1.5`, `abc`, item inexistente (`99999`) ou tentativa de inserir a mesma peça 2 vezes na mesma OS | `ControllersCadastrosEOrdensTests.test_itens_invalidos_inexistentes_e_duplicados_ct048_063_068` | Todas as tentativas inválidas ou duplicadas retornam HTTP `400` sem corromper o item existente | **PASSOU** |
| **Bloqueio de Manipulação de Preço/Status via POST** | H12, H13 | Cliente malicioso envia `preco_unitario_historico=0.01`, `total=0`, `status=aprovada` no POST de inclusão de item | `ControllersCadastrosEOrdensTests.test_preco_recebido_do_navegador_nao_altera_catalogo_ou_total` | Servidor ignora parâmetros forjados, grava preço oficial do catálogo (`30.00`), total `60.00` e mantém status `pendente` | **PASSOU** |
| **Bloqueio de Edição em OS Não-Pendente** | H13, H14 | Tentativa de adicionar/remover item ou mudar desconto em OS `aprovada`, `em_execucao` ou `concluida` | `ControllersCadastrosEOrdensTests.test_os_nao_pendente_bloqueia_toda_edicao` | Servidor retorna HTTP `400` e mantém itens e total bloqueados | **PASSOU** |

---

## 2. Evidências de Validação em Tempo Real no Frontend (`static/js/orcamento.js`)

1. **Inserção e Remoção Dinâmica N:N:**
   - Funções `adicionarLinhaPeca()`, `adicionarLinhaServico()` e `removerLinha(rowId, tipo)` manipulam o DOM sem recarregar a página, enviando arrays `pecas_id[]`, `pecas_qtd[]`, `servicos_id[]` e `servicos_qtd[]` no formulário POST.
2. **Cálculo Monetário Instantâneo e Bloqueio de Desconto Fora da Faixa:**
   - A função `calcularTotais()` recalcula a cada evento `input`/`change` os valores de `#subtotalPecas`, `#subtotalServicos`, `#subtotalGeral`, `#valorDesconto` e `#totalFinal` formatados em `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })`.
   - Caso o usuário digite um desconto menor que `0` ou maior que `100`, o campo recebe `.is-invalid`, a mensagem `#erroDesconto` é exibida e os botões `#btnAbrirModalConversao` e `#btnConverterOS` são imediatamente desabilitados (`disabled = true`).
3. **Modal de Confirmação e Prevenção de Duplo Clique (`H12`):**
   - Ao clicar em `"Converter em Ordem de Serviço"`, a função `validarOrcamentoAntesDeConverter()` verifica se Cliente, Veículo e ao menos um item foram selecionados sem duplicidade, exibe o modal `#modalConfirmarConversao` com o resumo da operação e, na confirmação do envio, desabilita o botão de submit com *spinner* de carregamento.

