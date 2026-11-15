# Relatório Individual de Contribuição — Sprint 4 (E8) e Fechamento (E9/E10)

**Aluno:** Rodrigo de Azevedo Junior  
**RA:** 2840482421044  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Desenvolvedor Frontend / Configuração Django & Deploy  
**Período:** 05/11/2026 a 25/11/2026  
**Sprint:** 4 (E8) + Fechamento Final (E9/E10)  

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 4 e etapa de fechamento do MVP, fui responsável pela construção do Dashboard Gerencial com gráficos interativos em Chart.js, integração final de todas as telas e rotas da equipe, revisão da documentação reproduzível (`README.md`) e consolidação do pacote de entrega acadêmica:

- **Dashboard Analítico do Dono/Gerente (`H19`, `H20`, `H21`):**
  - Desenvolvimento do template `templates/relatorios/dashboard.html` com filtro de período por data de conclusão (`inicio` e `fim`) e cards de indicadores executivos (Faturamento Líquido, OSs Concluídas, Ticket Médio por OS e Total em Descontos Concedidos).
  - Implementação do módulo JavaScript `static/js/dashboard_charts.js` integrado ao **Chart.js 4.4**, renderizando:
    1. Gráfico comparativo de **Faturamento Mensal Líquido vs. Descontos Concedidos** (`H19`) com formatação monetária BRL (`R$`).
    2. Gráfico horizontal e tabela classificada de **Serviços Mais Executados** (`H20`).
    3. Gráfico horizontal e tabela classificada de **Peças Mais Vendidas / Utilizadas** (`H21`).
  - Implementação de *empty states* amigáveis (`#emptyFaturamento`, `#emptyRankingServicos`, `#emptyRankingPecas`) quando o período filtrado não possui Ordens de Serviço concluídas (`CT-039`).

- **Integração Geral da Equipe e Testes Ponta a Ponta (`CT-058`):**
  - Consolidação das entregas de todas as branches da equipe (`Features/Felipe`, `feature/chen-sprints-1-2`, `joao-sprint1e2` e `Features/Rodrigo-Sprint-1/2`) na estrutura oficial do projeto.
  - Implementação e validação do teste automatizado de ponta a ponta (`test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058`) em `core/tests/test_sprints_regressao.py`.

- **Documentação Reproduzível e Deploy Final (`H23`, `H24`, `H25`):**
  - Revisão final do `README.md` com o mapa completo de diretórios das 4 Sprints, instruções de banco PostgreSQL/SQLite, execução de `setup_perfis` e comandos de teste (`python manage.py test` e `pytest`).
  - Consolidação do Checklist Final de Aceite do MVP (`docs/relatorio-final-mvp.md`) para a apresentação final (`E9/E10`).

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H19** (Faturamento Mensal Líquido) | Interface do relatório, KPIs e gráfico Chart.js de faturamento mensal | Concluída |
| **H20** (Serviços Mais Executados) | Tabela e gráfico horizontal de ranking de serviços com empty state | Concluída |
| **H21** (Peças Mais Vendidas) | Tabela e gráfico horizontal de ranking de peças com empty state | Concluída |
| **H23** (Consistência Visual Desktop) | Padronização responsiva, Sidebar por perfil e feedbacks em todas as telas | Concluída |
| **H24** (Deploy Público Contínuo) | Publicação e verificação de assets estáticos (WhiteNoise) e rotas em produção | Concluída |
| **H25** (README Reproduzível) | Revisão final do `README.md` cobrindo instalação, `.env`, migrações e testes | Concluída |

---

## 3. Evidências Técnicas (Arquivos, PRs e Testes)

- `templates/relatorios/dashboard.html` — Dashboard Analítico do Dono/Gerente (`H19`, `H20`, `H21`)
- `static/js/dashboard_charts.js` — Gráficos interativos Chart.js com formatação BRL
- `core/views.py` (`relatorios_dashboard`) e `core/urls.py` — Agregações sem duplicação N:N e desempate alfabético
- `core/tests/test_sprints_regressao.py` — Suíte de regressão e teste ponta a ponta (`CT-058`)
- `README.md` e `docs/relatorio-final-mvp.md` — Documentação técnica e checklist final das 25 histórias e 70 casos de teste

---

## 4. Autoavaliação e Lições Aprendidas

Fechar o ciclo de desenvolvimento construindo o Dashboard Gerencial mostrou como todas as decisões tomadas desde a Sprint 1 — como o congelamento do `preco_unitario_historico` nas tabelas associativas e o registro de `data_conclusao` na conclusão da OS pelo mecânico — são essenciais para gerar relatórios gerenciais confiáveis. A utilização de Django Templates (DTL) com Bootstrap 5 e Chart.js permitiu entregar uma interface limpa, rápida e 100% aderente aos requisitos da disciplina.

