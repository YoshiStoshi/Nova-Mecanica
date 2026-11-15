# Relatório Final e Checklist de Aceite do MVP (E9 / E10)

**Projeto:** Nova Mecânica — Sistema de Gestão para Oficina Mecânica  
**Disciplina:** Laboratório de Software 3 (Laboratório de Engenharia de Software) — Trilha B  
**Instituição:** FATEC Ribeirão Preto — Análise e Desenvolvimento de Sistemas (ADS)  
**URL de Produção (Render):** `https://nova-mecanica.onrender.com`  
**Repositório Oficial:** `https://github.com/YoshiStoshi/Nova-Mecanica`  

---

## 1. Equipe Oficial e Consolidação de Entregas

| Integrante | RA | Papel no Projeto | Sprints Entregues |
|---|---|---|---|
| **Rodrigo de Azevedo Junior** | `2840482421044` | Frontend (DTL / Bootstrap 5 / JS / Chart.js), Configuração Django & Deploy | Sprints 1, 2, 3 e 4 |
| **João Gabriel Cardoso Martarello** | `2840482421028` | Backend de Cadastros, Validadores, Motor Financeiro Decimal e Serviços de OS | Sprints 1, 2, 3 e 4 |
| **Felipe Delchiaro Malzoni** | `2840482421025` | Backend de Permissões, Estoque, Aprovação Atômica, Execução e Faturamento | Sprints 1, 2, 3 e 4 |
| **Carlos Chen** | `2840482421030` | Modelagem Relacional (`models.py`), DDL/Constraints PostgreSQL (`docs/database/`), Seeds e Testes de Integridade | Sprints 1, 2, 3 e 4 |

---

## 2. Checklist de Atendimento Integral do Backlog do Produto (H01 a H25)

| ID | História de Usuário | Sprint | Status | Rota / Módulo Principal |
|---|---|---|---|---|
| **H01** | Autenticação de usuários (Login e Logout seguro via POST com CSRF) | Sprint 1 | **CONCLUÍDA** | `/login/`, `/logout/` (`core/views.py`) |
| **H02** | Controle de acesso por perfil (`Dono/Gerente`, `Atendente`, `Mecânico`) | Sprint 1 | **CONCLUÍDA** | `setup_perfis.py`, decorators e `base.html` |
| **H03** | Cadastro e listagem de Clientes com validação matemática e normalização de CPF | Sprint 1 | **CONCLUÍDA** | `/clientes/`, `/clientes/novo/` (`core/validators.py`) |
| **H04** | Cadastro e listagem de Veículos vinculados a Clientes com validação de Placa (Antiga/Mercosul) | Sprint 1 | **CONCLUÍDA** | `/veiculos/`, `/veiculos/novo/` (`core/validators.py`) |
| **H05** | Consulta rápida ($< 3$s) do histórico de manutenção do veículo por placa | Sprint 3 | **CONCLUÍDA** | `/veiculos/historico/` (`historico_placa.html`) |
| **H06** | Cadastro e listagem de Peças no catálogo (exclusivo Dono/Gerente) | Sprint 1 | **CONCLUÍDA** | `/catalogo/pecas/` (`pecas_list_form.html`) |
| **H07** | Cadastro e listagem de Serviços no catálogo (exclusivo Dono/Gerente) | Sprint 1 | **CONCLUÍDA** | `/catalogo/servicos/` (`servicos_list_form.html`) |
| **H08** | Ajuste manual de saldo de estoque de peças com bloqueio de saldo negativo | Sprint 2 | **CONCLUÍDA** | `/catalogo/pecas/<pk>/ajustar-estoque/` |
| **H09** | Exclusão protegida de peças e serviços bloqueando itens vinculados a OSs | Sprint 2 | **CONCLUÍDA** | `/catalogo/pecas/<pk>/excluir/` (`PROTECT`) |
| **H10** | Montagem dinâmica de orçamento selecionando cliente, veículo, peças e serviços | Sprint 2 | **CONCLUÍDA** | `/orcamentos/novo/` (`orcamento_form.html`) |
| **H11** | Aplicação de desconto percentual ($0\%$ a $100\%$) e cálculo de total líquido em tempo real | Sprint 2 | **CONCLUÍDA** | `core/calculos.py`, `static/js/orcamento.js` |
| **H12** | Conversão de orçamento em Ordem de Serviço com status inicial `Pendente` sem baixar estoque | Sprint 2 | **CONCLUÍDA** | `/orcamentos/converter/` |
| **H13** | Associação N:N de Peças na OS com quantidade e congelamento do `preco_unitario_historico` | Sprint 2 | **CONCLUÍDA** | `ItemPeca` (`core/models.py`, `core/services.py`) |
| **H14** | Associação N:N de Serviços na OS com quantidade e congelamento do `preco_unitario_historico` | Sprint 2 | **CONCLUÍDA** | `ItemServico` (`core/models.py`, `core/services.py`) |
| **H15** | Aprovação de OS pelo Dono/Gerente com verificação e baixa atômica de estoque (`select_for_update`) | Sprint 3 | **CONCLUÍDA** | `/os/aprovar/`, `/os/<pk>/aprovar/` |
| **H16** | Painel do Mecânico com listagem das OSs do dia (`aprovada` e `em_execucao`) | Sprint 3 | **CONCLUÍDA** | `/mecanico/os-dia/` (`os_dia.html`) |
| **H17** | Confirmação de uso de peças pelo Mecânico até o limite aprovado **sem nova baixa de estoque** | Sprint 3 | **CONCLUÍDA** | `/mecanico/os/<pk>/pecas/<item_id>/confirmar/` |
| **H18** | Conclusão técnica da OS pelo Mecânico com registro automático de data e hora (`data_conclusao`) | Sprint 3 | **CONCLUÍDA** | `/mecanico/os/<pk>/concluir/` |
| **H19** | Relatório Gerencial de Faturamento Mensal Líquido (apenas OSs `concluida`, sem duplicação N:N) | Sprint 4 | **CONCLUÍDA** | `/relatorios/dashboard/` (`dashboard.html`) |
| **H20** | Ranking de Serviços Mais Executados com desempate alfabético por descrição | Sprint 4 | **CONCLUÍDA** | `/relatorios/dashboard/` (`dashboard_charts.js`) |
| **H21** | Ranking de Peças Mais Vendidas com desempate alfabético por descrição | Sprint 4 | **CONCLUÍDA** | `/relatorios/dashboard/` (`dashboard_charts.js`) |
| **H22** | Validações amigáveis de formulários com `is-invalid`, mensagens por campo e retenção de dados | Sprint 1 | **CONCLUÍDA** | `core/forms.py`, `includes/form_fields.html` |
| **H23** | Interface web responsiva com Sidebar (220px), Header sticky e identidade visual padronizada | Sprints 1–4| **CONCLUÍDA** | `templates/base.html`, `static/css/custom.css` |
| **H24** | Deploy público acessível por URL com Gunicorn, WhiteNoise e PostgreSQL | Sprints 1–4| **CONCLUÍDA** | `Procfile`, `setup/settings.py`, Render |
| **H25** | Documentação `README.md` reproduzível com instruções de setup, variáveis `.env` e testes | Sprints 1–4| **CONCLUÍDA** | `README.md`, `.env.example` |

---

## 3. Consolidação dos 70 Casos de Teste Homologados (E4b)

| Bloco de Testes (E4b) | Casos de Teste Cobertos | Arquivo de Evidência / Suíte Automatizada | Status Geral |
|---|---|---|---|
| **Autenticação e Controle de Acesso por Perfil** | `CT-001` a `CT-005`, `CT-043`, `CT-044` | `test_sprint1_sprint2.py`, `test_cadastros_e_ordens.py` ([Evidências Sprint 1](sprint-1-evidencias-teste.md)) | **100% APROVADO** |
| **Cadastro de Clientes, Veículos e Histórico por Placa** | `CT-006` a `CT-013`, `CT-055`, `CT-059`, `CT-067`, `CT-069`, `CT-070` | `test_cadastros_e_ordens.py`, `test_sprints_regressao.py` ([Evidências Sprint 1](sprint-1-evidencias-teste.md) / [Sprint 3](sprint-3-evidencias-teste.md)) | **100% APROVADO** |
| **Catálogo de Peças, Serviços, Estoque e Exclusão Protegida** | `CT-014` a `CT-018`, `CT-045`, `CT-048`, `CT-052`, `CT-053` | `test_sprint1_sprint2.py`, `test_chen_database.py` ([Evidências Sprint 2](sprint-2-evidencias-teste.md)) | **100% APROVADO** |
| **Orçamento Dinâmico, Desconto (0–100%), N:N e Preço Histórico** | `CT-019` a `CT-025`, `CT-049` a `CT-051`, `CT-054`, `CT-063`, `CT-064`, `CT-068` | `test_cadastros_e_ordens.py`, `test_sprint1_sprint2.py`, `test_chen_database.py` ([Evidências Sprint 2](sprint-2-evidencias-teste.md)) | **100% APROVADO** |
| **Aprovação de OS, Baixa Atômica, Concorrência e Fluxo do Mecânico** | `CT-026` a `CT-036`, `CT-046`, `CT-047`, `CT-060` a `CT-062` | `test_sprints_regressao.py` ([Evidências Sprint 3](sprint-3-evidencias-teste.md)) | **100% APROVADO** |
| **Relatórios Gerenciais (Faturamento e Rankings) e Fluxo E2E** | `CT-037` a `CT-042`, `CT-056` a `CT-058`, `CT-065`, `CT-066` | `test_sprints_regressao.py` ([Evidências Sprint 4](sprint-4-evidencias-teste.md)) | **100% APROVADO** |

---

## 4. Roteiro de Demonstração para a Apresentação Final (E9 / E10)

1. **Acesso e Perfis (`H01`, `H02`):** Entrar como `Atendente` e demonstrar o menu restrito ao fluxo operacional; tentar acessar `/catalogo/pecas/` ou `/relatorios/dashboard/` para evidenciar o bloqueio de segurança.
2. **Cadastros e Histórico (`H03`, `H04`, `H05`):** Cadastrar um Cliente (com validação de CPF) e seu Veículo (placa Mercosul), e consultar `/veiculos/historico/` demonstrando os estados de placa inexistente, veículo sem histórico e veículo com histórico.
3. **Orçamento Dinâmico e Conversão (`H10` a `H14`):** Em `/orcamentos/novo/`, selecionar o cliente e veículo, adicionar múltiplas peças e serviços dinamicamente, aplicar desconto percentual em tempo real e confirmar no modal a conversão em **OS Pendente** (mostrando que o estoque permanece intacto).
4. **Aprovação e Baixa Atômica (`H06`, `H08`, `H15`):** Entrar como `Dono/Gerente`, acessar `/os/aprovar/`, demonstrar o bloqueio visual quando falta estoque, ajustar o saldo em `/catalogo/pecas/` e aprovar a OS (comprovando a baixa atômica única).
5. **Execução na Oficina (`H16`, `H17`, `H18`):** Entrar como `Mecânico`, acessar `/mecanico/os-dia/`, confirmar a quantidade de peças utilizadas (comprovando que não há nova baixa no estoque) e clicar em **Concluir OS**.
6. **Dashboard Gerencial (`H19`, `H20`, `H21`):** Retornar ao perfil `Dono/Gerente` em `/relatorios/dashboard/` e apresentar o Faturamento Líquido atualizado no gráfico Chart.js e os Rankings de Serviços e Peças.
