# Relatório de Entrega da Sprint 4 (E8) — Documento Capa

**Projeto:** Nova Mecânica — Sistema de Gestão para Oficina Mecânica  
**Disciplina:** Laboratório de Software 3 (Laboratório de Engenharia de Software) — Trilha B  
**Instituição:** FATEC Ribeirão Preto — Curso de Análise e Desenvolvimento de Sistemas (ADS)  
**Sprint:** 4 (E8) — Dashboard Analítico, Relatórios Gerenciais (`H19`, `H20`, `H21`), Regressão e Homologação Final  
**Período da Sprint:** 05/11/2026 a 25/11/2026  
**Pontuação Planejada vs. Entregue:** 7 Story Points / 7 Story Points (100%) + Homologação Integral do MVP  
**URL de Produção / Homologação (Render):** `https://nova-mecanica.onrender.com`  
**Repositório Oficial:** `https://github.com/YoshiStoshi/Nova-Mecanica`  

---

## 1. Identificação da Equipe Oficial

| Integrante | RA | Papel Principal na Sprint 4 | Relatório Individual |
|---|---|---|---|
| **Rodrigo de Azevedo Junior** | `2840482421044` | Dashboard Gerencial (`dashboard.html`), Gráficos Chart.js (`dashboard_charts.js`), Revisão Final do `README.md` (`H25`) e Deploy Final (`H24`) | [sprint-4-contribuicao-rodrigo.md](sprint-4-contribuicao-rodrigo.md) |
| **Felipe Delchiaro Malzoni** | `2840482421025` | Endpoint Analítico de Faturamento Mensal (`core/views.py`) e Bateria de Testes de Regressão (`SprintRegressaoTests`) | [sprint-4-contribuicao-felipe.md](sprint-4-contribuicao-felipe.md) |
| **João Gabriel Cardoso Martarello** | `2840482421028` | Queries Agregadas de Ranking (`H20`, `H21`) com Desempate Alfabético e Testes Ponta a Ponta (`CT-058`) | [joao-sprint1e2.md](joao-sprint1e2.md) |
| **Carlos Chen** | `2840482421030` | Otimização de Consultas Analíticas sem Duplicação por Joins N:N e Validação Final de Integridade Relacional no PostgreSQL | [sprint-2-contribuicao-chen.md](sprint-2-contribuicao-chen.md) |

---

## 2. Escopo da Sprint 4: Planejado vs. Entregue (7 Pontos + Fechamento)

| ID | História de Usuário (Backlog E2) | Pontos | Planejado | Entregue | Evidência Principal no Repositório |
|---|---|---|---|---|---|
| **H19** | Relatório de Faturamento Mensal Líquido exclusivo para Dono/Gerente considerando apenas OSs `concluida` | 3 pts | Sim | **100% Concluída** | `core/views.py` (`relatorios_dashboard`, `faturamento_mensal`), `templates/relatorios/dashboard.html` |
| **H20** | Ranking de Serviços Mais Executados com ordenação decrescente e desempate alfabético por descrição | 2 pts | Sim | **100% Concluída** | `core/views.py` (`relatorios_dashboard`), `templates/relatorios/dashboard.html`, `static/js/dashboard_charts.js` |
| **H21** | Ranking de Peças Mais Vendidas com ordenação decrescente e desempate alfabético por descrição | 2 pts | Sim | **100% Concluída** | `core/views.py` (`relatorios_dashboard`), `templates/relatorios/dashboard.html`, `static/js/dashboard_charts.js` |
| **H23** | Consistência de layout desktop, navegação fluida e feedback visual em todas as telas do MVP | Transversal | Sim | **100% Concluída** | `templates/base.html`, `static/css/custom.css` |
| **H24 / H25** | Homologação final em produção no Render e documentação técnica `README.md` 100% reproduzível | Transversal | Sim | **100% Concluída** | `README.md`, `Procfile`, `docs/relatorio-final-mvp.md` |

---

## 3. Regras Analíticas e de Negócio Garantidas na Sprint 4

1. **Exatidão Contábil do Faturamento Mensal (`H19`, `CT-037`, `CT-038`, `CT-065`):**
   - Soma exclusivamente as Ordens de Serviço com `status='concluida'`, agrupadas pelo mês de conclusão (`TruncMonth`).
   - Computa o valor líquido final (`total`, já deduzido o `valor_desconto` percentual).
   - A agregação é executada diretamente sobre a tabela `OrdemServico` antes de qualquer junção com `ItemPeca` ou `ItemServico`, **eliminando 100% do risco de multiplicação de valores por relacionamento N:N**.
2. **Rankings de Serviços (`H20`) e Peças (`H21`) com Desempate Determinístico (`CT-040`, `CT-041`, `CT-066`):**
   - Consideram apenas itens pertencentes a OSs com `status='concluida'` no período filtrado.
   - Ordenam de forma decrescente pela soma de quantidades (`-quantidade_executada` / `-quantidade_vendida`) e utilizam a descrição (`servico__descricao` / `peca__descricao`) como critério de desempate em ordem alfabética crescente.
3. **Estados Vazios Amigáveis (`CT-039`) e Restrição de Perfil (`CT-042`):**
   - Quando não há OSs concluídas no período filtrado, o Dashboard exibe estados vazios informativos (`#emptyFaturamento`, `#emptyRankingServicos`, `#emptyRankingPecas`) sem erros de divisão por zero no cálculo do Ticket Médio.
   - Qualquer tentativa de acesso por `Atendente`, `Mecânico` ou usuário anônimo às rotas de relatório é bloqueada no servidor (`HTTP 403 Forbidden` / redirecionamento de login).

---

## 4. Resumo dos Testes da Sprint 4 e Homologação Final

As evidências detalhadas encontram-se em [sprint-4-evidencias-teste.md](sprint-4-evidencias-teste.md) e no checklist consolidado [relatorio-final-mvp.md](relatorio-final-mvp.md).

| Caso de Teste | Cenário Validado | Status |
|---|---|---|
| **CT-037** | Faturamento mensal soma apenas OSs com status `concluida` e considera o valor líquido com desconto | **APROVADO** |
| **CT-038** | Exclusão de OSs com status `pendente`, `aprovada`, `em_execucao` ou `cancelada` do cálculo de faturamento | **APROVADO** |
| **CT-039** | Exibição de estado vazio amigável e Ticket Médio `R$ 0,00` quando não há OSs concluídas no período | **APROVADO** |
| **CT-040** | Ranking de Serviços Mais Executados (`H20`) ordenado decrescente por quantidade executada | **APROVADO** |
| **CT-041** | Ranking de Peças Mais Vendidas (`H21`) ordenado decrescente por unidades vendidas | **APROVADO** |
| **CT-042** | Bloqueio de acesso ao Dashboard Gerencial e endpoints de relatório para `Atendente` e `Mecânico` (`HTTP 403`) | **APROVADO** |
| **CT-058** | Fluxo completo Ponta a Ponta (E2E): Cliente $\rightarrow$ Veículo $\rightarrow$ Catálogo $\rightarrow$ Orçamento $\rightarrow$ OS Pendente $\rightarrow$ Aprovação/Baixa $\rightarrow$ Execução/Conclusão $\rightarrow$ Faturamento/Rankings | **APROVADO** |
| **CT-065** | Não duplicação do valor da OS no faturamento mensal quando a OS possui múltiplas peças e múltiplos serviços (N:N) | **APROVADO** |
| **CT-066** | Desempate alfabético por `descricao` nos rankings de Serviços (`H20`) e Peças (`H21`) quando quantidades empatam | **APROVADO** |
