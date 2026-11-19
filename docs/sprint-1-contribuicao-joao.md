# Relatório Individual de Contribuição — Sprint 1 (E5)

**Aluno:** João Gabriel Cardoso Martarello<br>
**RA:** 2840482421028<br>
**Projeto:** Nova Mecânica<br>
**Papel no Semestre:** Desenvolvedor Backend / UI Bootstrap<br>
**Período:** 21/08/2026 a 22/09/2026<br>
**Sprint:** 1 (E5)

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 1, atuei no backend dos cadastros de clientes e veículos e na padronização dos formulários com validações e feedback visual:

- **Cadastro de Clientes (`H03`):**
  - Implementação do `ClienteForm` em `core/forms.py` com os campos de nome, CPF, telefone e e-mail.
  - Integração das views `clientes` e `cliente_criar` em `core/views.py` para listagem e cadastro.
  - Tratamento de CPF duplicado sem perder os demais valores preenchidos no formulário.
  - Implementação de `normalizar_cpf` em `core/validators.py`, validando os dígitos verificadores e persistindo somente os 11 números.

- **Cadastro de Veículos (`H04`):**
  - Implementação do `VeiculoForm` com vínculo obrigatório a um cliente existente.
  - Integração das views `veiculos` e `veiculo_criar` para listagem e cadastro de veículos.
  - Implementação de `normalizar_placa`, aceitando os padrões antigo (`ABC-1234`) e Mercosul (`ABC1D23`) e armazenando a placa em maiúsculas e sem separadores.
  - Bloqueio de placas repetidas e preservação do vínculo correto entre cliente e veículo.

- **UI Bootstrap e Validações de Formulário (`H22`):**
  - Criação do `BootstrapFormMixin` em `core/forms_login.py` para aplicar `form-control`, `form-select`, `is-invalid` e atributos de acessibilidade aos campos Django.
  - Padronização de `ClienteForm`, `VeiculoForm` e `LoginForm` com componentes Bootstrap.
  - Exibição de mensagens próximas aos campos inválidos e retenção dos valores válidos após erro de submissão.
  - Uso do helper `cadastro` para centralizar renderização, persistência transacional e tratamento de duplicidade.

- **Testes Automatizados:**
  - Criação de testes de cadastro válido de cliente e múltiplos veículos.
  - Cobertura de CPF e placa inválidos, duplicados e normalizados.
  - Verificação de campos obrigatórios, e-mail inválido, retenção dos dados e proteção das rotas por autenticação/permissão.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H03** (Cadastro de Clientes) | Formulário, controller, normalização e validação de CPF | Concluída |
| **H04** (Cadastro de Veículos) | Formulário, controller, vínculo com cliente e validação de placa | Concluída |
| **H22** (Validações de Formulário) | Bootstrap, mensagens por campo e retenção dos dados | Concluída |

---

## 3. Evidências Técnicas

- `core/forms.py` — `ClienteForm` e `VeiculoForm`.
- `core/forms_login.py` — `BootstrapFormMixin` e `LoginForm`.
- `core/validators.py` — `normalizar_cpf` e `normalizar_placa`.
- `core/views.py` — Views de clientes, veículos e helper `cadastro`.
- `core/tests/test_cadastros_e_ordens.py` — Testes de cadastros, validadores, duplicidade e permissões.
- **Commit:** `82aa9e5` — implementação de cadastros, cálculos e validações.
- **Pull Request:** `PR #2` — integração da branch `joao-sprint1e2` na `main`.
- **Comando de validação:** `python manage.py test core.tests.test_cadastros_e_ordens`

---

## 4. Autoavaliação e Lições Aprendidas

A Sprint 1 reforçou a importância de validar e normalizar os dados antes da persistência. Centralizar o comportamento visual dos formulários no `BootstrapFormMixin` reduziu repetição e manteve o feedback de erros consistente. Nos cadastros, o tratamento de duplicidade dentro de uma transação permitiu apresentar mensagens claras sem descartar os valores já preenchidos pelo usuário.
