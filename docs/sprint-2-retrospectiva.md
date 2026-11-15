# Ata de Retrospectiva — Sprint 2 (E6)

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Data da Reunião:** 14/10/2026  
**Sprint Avaliada:** Sprint 2 (E6) — Período de 23/09/2026 a 14/10/2026  
**Participantes:**
- Rodrigo de Azevedo Junior (RA: 2840482421044)
- João Gabriel Cardoso Martarello (RA: 2840482421028)
- Felipe Delchiaro Malzoni (RA: 2840482421025)
- Carlos Chen (RA: 2840482421030)

---

## 1. O Que Funcionou Bem (Keep Doing)

1. **Ergonomia e Velocidade na Montagem de Orçamento (`orcamento_form.html` + `orcamento.js`):**
   - A tela dinâmica desenvolvida pelo Rodrigo com filtro instantâneo de veículos por cliente, adição/remoção de linhas N:N sem reload de página e resumo financeiro lateral sticky em tempo real cumpriu com folga a meta de usabilidade (montagem completa de orçamento em menos de 1 minuto, bem abaixo do limite de 5 minutos da `H10`).
2. **Motor Financeiro Determinístico (`core/calculos.py` e `core/services.py`):**
   - A centralização da regra de negócio em `calcular_totais` e `recalcular_ordem` usando `Decimal` e `ROUND_HALF_UP` garantiu 100% de consistência entre o valor exibido no orçamento e o valor gravado na Ordem de Serviço.
3. **Congelamento de Preço Histórico e Proteção de Exclusão (`H09`, `H13`, `H14`):**
   - O uso de `preco_unitario_historico` nas tabelas `ItemPeca` e `ItemServico` combinado com `on_delete=models.PROTECT` e validação prévia (`peca.itens_os.exists()`) blindou o histórico contábil da oficina contra alterações de preço ou exclusões acidentais no catálogo.
4. **Suíte de Testes de Casos de Borda:**
   - Os testes cobrindo manipulação maliciosa de parâmetros POST (tentativa de enviar preço `0.01` ou status `aprovada` pelo navegador), descontos limítrofes ($0\%$ e $100\%$) e rollback transacional garantiram alta confiabilidade.

---

## 2. O Que Pode Melhorar (Problems / Bottlenecks)

1. **Integração dos Scripts de Banco e Módulos Auxiliares:**
   - Assim como na Sprint 1, foi necessário consolidar os scripts SQL de constraints (`docs/database/`) e conectar os endpoints auxiliares de `sprint2_backend.py` ao roteamento principal (`core/urls.py`) para manter toda a base de código unificada na branch `main`.
2. **Preparação dos Campos de Model para a Sprint 3:**
   - Identificamos que a aprovação atômica da OS (`H15`), a confirmação de peças pelo mecânico (`H17`) e a conclusão com timestamp (`H18`) exigiriam novos campos em `OrdemServico` (`estoque_baixado`, `aprovada_em`, `data_conclusao`) e `ItemPeca` (`quantidade_utilizada`), que já foram mapeados e migrados.

---

## 3. Plano de Ação para a Sprint 3 (Action Items)

| Ação Definida | Responsável | Meta / Prazo |
|---|---|---|
| Implementar a view e interface de aprovação da OS pelo Dono/Gerente com baixa atômica de estoque (`select_for_update`) e destaque visual de peças insuficientes (`H15`) | Rodrigo, João & Felipe | Semana 1 da Sprint 3 |
| Desenvolver a busca de histórico de manutenções do veículo por placa para o Atendente com tempo de resposta $< 3$s (`H05`) | Rodrigo & João | Semana 1 da Sprint 3 |
| Construir o Painel do Mecânico com fila de OSs do dia (`H16`), confirmação de peças sem nova baixa (`H17`) e conclusão com registro de data/hora (`H18`) | Felipe, João & Rodrigo | Semana 2 da Sprint 3 |
| Validar os testes de concorrência e bloqueio de dupla baixa de estoque | Carlos Chen & Felipe | Semana 2 da Sprint 3 |

---

## 4. Métricas de Fechamento da Sprint 2

- **Histórias Planejadas:** 7 (`H08`, `H09`, `H10`, `H11`, `H12`, `H13`, `H14`)
- **Histórias Concluídas (Done):** 7 (100% de cumprimento do escopo da Sprint 2)
- **Total Acumulado no Semestre (Sprint 1 + Sprint 2):** 16 histórias concluídas e homologadas.

