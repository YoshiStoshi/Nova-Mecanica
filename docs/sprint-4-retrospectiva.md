# Ata de Retrospectiva Final — Sprint 4 (E8) e Fechamento do Semestre

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Data da Reunião:** 25/11/2026  
**Sprint Avaliada:** Sprint 4 (E8) — Período de 05/11/2026 a 25/11/2026  
**Participantes:**
- Rodrigo de Azevedo Junior (RA: 2840482421044)
- João Gabriel Cardoso Martarello (RA: 2840482421028)
- Felipe Delchiaro Malzoni (RA: 2840482421025)
- Carlos Chen (RA: 2840482421030)

---

## 1. O Que Funcionou Bem na Sprint 4 e no Projeto (Keep Doing)

1. **Dashboard Analítico com Chart.js (`templates/relatorios/dashboard.html` e `static/js/dashboard_charts.js`):**
   - A combinação de gráficos visuais interativos com tabelas analíticas e KPIs de topo (Faturamento Líquido, OSs Concluídas, Ticket Médio e Descontos Concedidos) entregou uma visão executiva clara e imediata para o perfil `Dono/Gerente`.
2. **Prevenção de Duplicação em Agregações SQL (`CT-065`) e Desempate Determinístico (`CT-066`):**
   - A decisão arquitetural de persistir `subtotal`, `valor_desconto` e `total` diretamente na `OrdemServico` tornou a consulta de faturamento mensal imune ao efeito multiplicador dos joins N:N com `ItemPeca` e `ItemServico`.
   - O critério secundário de ordenação `.order_by('-quantidade_executada', 'servico__descricao')` e `.order_by('-quantidade_vendida', 'peca__descricao')` garantiu resultados 100% determinísticos nos testes automatizados.
3. **Validação Ponta a Ponta (`CT-058`):**
   - O teste integrado de ponta a ponta percorreu todo o ciclo de vida de uma Ordem de Serviço através dos três perfis (`Atendente`, `Dono/Gerente` e `Mecânico`), comprovando que todas as 4 Sprints funcionam como um sistema único e coeso.

---

## 2. Lições Aprendidas ao Longo das 4 Sprints (E5 a E8)

1. **Regras Financeiras e de Estoque Exigem Barreira Dupla (Aplicação + Banco):**
   - Validar regras críticas tanto nos formulários/serviços do Django (`Decimal`, `ROUND_HALF_UP`, `select_for_update`) quanto nas constraints do banco (`UniqueConstraint`, `PROTECT`, `CHECK`) evitou qualquer inconsistência de saldo ou perda de histórico de preços.
2. **Automação de Setup (`setup_perfis`) e Testes Contínuos:**
   - Ter um comando único para provisionar grupos e permissões e uma suíte automatizada de testes reduziu drasticamente o tempo de homologação a cada merge na branch `main`.
3. **Documentação Contínua na Pasta `docs/`:**
   - Manter os relatórios de entrega, atas de retrospectiva, relatórios individuais e evidências de casos de teste organizados por Sprint facilitou a auditoria final para as etapas `E9` e `E10`.

---

## 3. Fechamento Final do MVP (Rumo à Apresentação E9 / E10)

- **Histórias do Backlog do Produto (H01 a H25):** 25 de 25 concluídas (100%).
- **Casos de Teste do Plano Oficial (E4b — CT-001 a CT-070):** 100% atendidos e homologados.
- **Status do Ambiente de Produção (Render):** Ativo, sincronizado com a branch `main` e pronto para demonstração ao vivo.
