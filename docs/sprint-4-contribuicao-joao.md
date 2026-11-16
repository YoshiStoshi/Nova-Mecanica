# Relatório Individual de Contribuição — Sprint 4 (E8)

**Aluno:** João Gabriel Cardoso Martarello<br>
**RA:** 2840482421028<br>
**Projeto:** Nova Mecânica<br>
**Papel no Semestre:** Desenvolvedor Backend / UI Bootstrap<br>
**Período:** 05/11/2026 a 25/11/2026<br>
**Sprint:** 4 (E8)

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 4, atuei nas consultas agregadas dos rankings gerenciais e no tratamento visual de períodos sem dados:

- **Serviços Mais Executados (`H20`):**
  - Consolidação da consulta em `relatorios_dashboard`, considerando somente itens vinculados a Ordens de Serviço concluídas no período selecionado.
  - Agrupamento por serviço com `Sum('quantidade')` e `Count('ordem_id', distinct=True)`.
  - Ordenação decrescente pela quantidade executada e desempate alfabético por descrição.
  - Cálculo da receita histórica usando quantidade e `preco_unitario_historico`, sem depender do preço atual do catálogo.

- **Peças Mais Vendidas (`H21`):**
  - Consolidação da consulta agregada por peça, somando as quantidades registradas nas OSs concluídas.
  - Ordenação decrescente por unidades vendidas e desempate alfabético por descrição.
  - Preservação do valor histórico de cada item para exibição da receita associada ao ranking.

- **Views e Estados Vazios:**
  - Integração dos rankings ao template `templates/relatorios/dashboard.html` em tabelas independentes para serviços e peças.
  - Tratamento separado dos estados vazios: o dashboard informa quando não existem serviços executados ou peças vendidas no período, sem tentar renderizar gráficos sem dados.
  - Manutenção dos indicadores numéricos em zero quando o filtro não encontra OSs concluídas.

- **Testes Automatizados:**
  - Validação de que OSs pendentes não participam dos rankings.
  - Verificação da soma das quantidades, da ordenação dos resultados e do desempate alfabético.
  - Verificação das mensagens de estado vazio para serviços e peças.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H20** (Serviços Mais Executados) | Consulta agregada, ordenação, view e estado vazio | Concluída |
| **H21** (Peças Mais Vendidas) | Consulta agregada, ordenação, view e estado vazio | Concluída |

---

## 3. Evidências Técnicas

- `core/views.py` (`relatorios_dashboard`) — Consultas agregadas de serviços e peças.
- `templates/relatorios/dashboard.html` — Tabelas dos rankings e estados vazios independentes.
- `core/tests/test_joao_sprints_3_4.py`:
  - `test_h20_h21_rankings_agregam_somente_os_concluidas`
  - `test_h20_h21_dashboard_exibe_estados_vazios`
- **Comando de validação:** `python manage.py test core.tests.test_joao_sprints_3_4`
- **Resultado:** 4 testes do escopo aprovados; suíte completa com 58 testes aprovados e 1 teste PostgreSQL ignorado no ambiente SQLite.
- **Situação:** alterações validadas localmente e pendentes de commit/PR.

---

## 4. Autoavaliação e Lições Aprendidas

As consultas dos rankings reforçaram que agregações em relacionamentos N:N precisam partir dos itens da OS e considerar apenas ordens concluídas, evitando que registros pendentes distorçam os resultados. O desempate alfabético tornou a ordenação determinística, enquanto os estados vazios independentes permitiram que o dashboard permanecesse compreensível mesmo quando apenas uma das categorias possuía dados.
