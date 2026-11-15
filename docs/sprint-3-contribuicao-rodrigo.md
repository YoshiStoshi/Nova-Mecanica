# Relatório Individual de Contribuição — Sprint 3 (E7)

**Aluno:** Rodrigo de Azevedo Junior  
**RA:** 2840482421044  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Desenvolvedor Frontend / Configuração Django & Deploy  
**Período:** 15/10/2026 a 04/11/2026  
**Sprint:** 3 (E7)  

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 3, fui responsável pelo desenvolvimento das interfaces operacionais de aprovação de Ordem de Serviço, consulta rápida de histórico veicular por placa e painel de execução do mecânico, além da integração das rotas e atualização do deploy:

- **Interface de Aprovação de OS e Conferência de Saldo (`H15`):**
  - Desenvolvimento do template `templates/os/aprovar_os.html` exclusivo para o perfil `Dono/Gerente`.
  - Criação do painel comparativo linha a linha exibindo a quantidade solicitada na OS versus o saldo atual em estoque (`Peca.estoque`), com badges semânticos verdes (`Disponível`) e vermelhos (`Insuficiente -X un`).
  - Bloqueio visual automático do botão `"Aprovar OS e Baixar Estoque"` (`disabled`) e exibição de alerta detalhado com atalho para reposição quando qualquer peça apresenta saldo insuficiente (`CT-027`, `CT-046`).

- **Tela de Consulta Rápida de Histórico por Placa (`H05`):**
  - Desenvolvimento do template `templates/veiculos/historico_placa.html` com barra de busca normalizada em tempo real para maiúsculas e chips de acesso rápido às placas cadastradas.
  - Implementação de estados visuais distintos para:
    1. **Placa não cadastrada no sistema (`CT-012`):** card de alerta com botão direto para cadastrar novo veículo.
    2. **Veículo cadastrado sem histórico de manutenção (`CT-059`):** exibição da ficha completa do veículo/proprietário acompanhada de estado vazio informativo e botão para abrir o primeiro orçamento.
    3. **Veículo com histórico (`CT-011`):** linha do tempo das OSs com status, datas de abertura/conclusão, peças e serviços com preços unitários históricos congelados e total acumulado.

- **Painel Operacional do Mecânico (`H16`, `H17`, `H18`):**
  - Desenvolvimento do template `templates/mecanico/os_dia.html` apresentando os indicadores do dia e os cards das OSs com status `aprovada` e `em_execucao`.
  - Criação dos formulários inline de confirmação de quantidade de peças utilizadas (`0` até o limite aprovado na OS) com feedback visual de progresso e sem acionar nova baixa de estoque (`H17`).
  - Implementação do botão de conclusão técnica da OS (`H18`) registrando data e hora de encerramento e movendo a ordem para a tabela de concluídas do dia.

- **Navegação por Perfil e Testes de Integração:**
  - Atualização da Sidebar em `templates/base.html` para exibir dinamicamente os links de `Aprovar OS`, `Histórico por Placa` e `Fila do Mecânico` de acordo com o perfil autenticado.
  - Integração das views e testes automatizados em `core/views.py`, `core/urls.py` e `core/tests/test_sprints_regressao.py`.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H05** (Histórico por Placa $< 3$s) | Template `historico_placa.html`, normalização JS e distinção dos 3 estados | Concluída |
| **H15** (Aprovação e Baixa Atômica) | Template `aprovar_os.html`, destaque de peças insuficientes e bloqueio visual | Concluída |
| **H16** (Fila do Dia do Mecânico) | Template `os_dia.html` com listagem de OSs aprovadas e em execução | Concluída |
| **H17** (Confirmação de Uso de Peças) | Interface de confirmação de quantidade aplicada sem nova baixa de estoque | Concluída |
| **H18** (Conclusão da OS com Data/Hora)| Ação de encerramento da OS e tabela de OSs concluídas no dia | Concluída |

---

## 3. Evidências Técnicas (Arquivos, PRs e Testes)

- `templates/os/aprovar_os.html` — Painel de conferência de estoque e aprovação de OS (`H15`)
- `templates/veiculos/historico_placa.html` — Consulta de histórico veicular por placa (`H05`)
- `templates/mecanico/os_dia.html` — Fila de execução, confirmação de peças e conclusão do mecânico (`H16`, `H17`, `H18`)
- `core/views.py` e `core/urls.py` — Views e rotas integradas com controle de perfil e transações atômicas
- `core/tests/test_sprints_regressao.py` — Testes automatizados cobrindo os fluxos da Sprint 3

---

## 4. Autoavaliação e Lições Aprendidas

A construção do painel de aprovação de OS (`aprovar_os.html`) evidenciou a importância de alinhar a experiência visual (UX) com as regras transacionais do banco de dados: mostrar exatamente qual peça está com saldo insuficiente e quantas unidades faltam evita que o gestor tente aprovar uma OS às cegas. Da mesma forma, no painel do mecânico, deixar claro na interface que o estoque já foi baixado na aprovação ajudou a traduzir a regra de negócio `H17` em uma operação simples e livre de erros.

