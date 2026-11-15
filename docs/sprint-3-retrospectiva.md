# Ata de Retrospectiva — Sprint 3 (E7)

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Data da Reunião:** 04/11/2026  
**Sprint Avaliada:** Sprint 3 (E7) — Período de 15/10/2026 a 04/11/2026  
**Participantes:**
- Rodrigo de Azevedo Junior (RA: 2840482421044)
- João Gabriel Cardoso Martarello (RA: 2840482421028)
- Felipe Delchiaro Malzoni (RA: 2840482421025)
- Carlos Chen (RA: 2840482421030)

---

## 1. O Que Funcionou Bem (Keep Doing)

1. **Clareza Visual no Painel de Aprovação de OS (`templates/os/aprovar_os.html`):**
   - A tela desenvolvida pelo Rodrigo exibe lado a lado a fila de OSs pendentes e a tabela comparativa entre quantidade solicitada e saldo disponível em estoque, destacando em vermelho (`table-danger` + badge `Insuficiente`) qualquer item faltante e desabilitando o botão de aprovação antes mesmo do envio.
2. **Transação Atômica e Prevenção de Dupla Baixa (`H15` e `H17`):**
   - A implementação conjunta de `select_for_update()` e da flag `estoque_baixado` garantiu que a baixa ocorra única e exclusivamente na aprovação pelo Dono/Gerente (`H15`), enquanto o painel do mecânico (`H17`) registra o consumo real em `quantidade_utilizada` sem tocar em `Peca.estoque`.
3. **Distinção Semântica na Consulta de Histórico por Placa (`H05`):**
   - A separação explícita entre os estados *"Placa não cadastrada no sistema"* (`CT-012`) e *"Veículo sem histórico de manutenção"* (`CT-059`) melhorou a experiência do Atendente no balcão e atendeu integralmente aos critérios de aceite da especificação de testes.

---

## 2. O Que Pode Melhorar (Problems / Bottlenecks)

1. **Sincronização da Nova Migration (`0002_ordemservico_campos_sprint3_4.py`):**
   - A inclusão dos campos `estoque_baixado`, `aprovada_em`, `data_conclusao` e `quantidade_utilizada` exigiu alinhar todos os integrantes para rodar `python manage.py migrate` antes de testar os fluxos de conclusão da OS.
2. **Padronização de Respostas HTML vs. JSON:**
   - Como o backend possuía tanto endpoints de API JSON (`sprint3_backend.py`) quanto views DTL com `messages` e `redirect` (`core/views.py`), mantivemos ambos ativos e roteados em `core/urls.py`, garantindo 100% de compatibilidade com todos os testes automatizados da equipe.

---

## 3. Plano de Ação para a Sprint 4 (Action Items)

| Ação Definida | Responsável | Meta / Prazo |
|---|---|---|
| Desenvolver o Dashboard Gerencial (`templates/relatorios/dashboard.html`) e gráficos Chart.js (`static/js/dashboard_charts.js`) para `H19`, `H20` e `H21` | Rodrigo | Semana 1 da Sprint 4 |
| Garantir que a query de Faturamento Mensal (`H19`) agrupe exclusivamente OSs `concluida` sem duplicação por N:N e que os rankings (`H20`, `H21`) tenham desempate alfabético por descrição | Felipe, João & Carlos Chen | Semana 1 da Sprint 4 |
| Executar a bateria completa de regressão e o teste ponta a ponta (`CT-058`) consolidando o Checklist Final do MVP (`E9/E10`) | Toda a Equipe | Semana 2 da Sprint 4 |

---

## 4. Métricas de Fechamento da Sprint 3

- **Histórias Planejadas:** 5 (`H05`, `H15`, `H16`, `H17`, `H18` — 15 Story Points)
- **Histórias Concluídas (Done):** 5 (100% de cumprimento do escopo da Sprint 3)
- **Total Acumulado no Semestre (Sprints 1 a 3):** 21 histórias concluídas.
