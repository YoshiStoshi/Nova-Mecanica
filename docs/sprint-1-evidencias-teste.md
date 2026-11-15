# Evidências de Testes e Deploy — Sprint 1 (E5)

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Sprint:** 1 (E5) — Período: 21/08/2026 a 22/09/2026  
**Suítes de Teste Executadas:**
- `core/tests/test_sprint1_sprint2.py`
- `core/tests/test_cadastros_e_ordens.py`
- `core/tests/test_chen_database.py`

**Comando de Execução Reproduzível:**
```bash
python manage.py test
```

---

## 1. Matriz de Rastreabilidade e Resultados (Casos de Teste da Sprint 1)

| ID do Caso de Teste | História | Cenário Testado | Método Automatizado | Resultado Obtido | Status |
|---|---|---|---|---|---|
| **CT-001** | H01, H02 | Login com perfil `Dono/Gerente` redireciona ao Dashboard e exibe menu de Catálogo | `Sprint1e2Tests.test_login_sucesso_e_logout_invalida_sessao_ct043` / `test_catalogo_pecas_somente_dono_gerente_h06` | Redirecionamento HTTP 302 para `/` e HTTP 200 em `/catalogo/pecas/` | **PASSOU** |
| **CT-002** | H01, H02 | Login com perfil `Atendente` acessa Clientes, Veículos e OS, mas é bloqueado no Catálogo | `ControllersCadastrosEOrdensTests.test_paginas_e_perfis` / `Sprint1e2Tests.test_catalogo_pecas_somente_dono_gerente_h06` | HTTP 200 nas rotas operacionais; redirecionamento com alerta ao tentar acessar `/catalogo/pecas/` | **PASSOU** |
| **CT-003** | H01, H02 | Login com perfil `Mecânico` bloqueado em rotas de cadastro de clientes, veículos e edição de OS | `ControllersCadastrosEOrdensTests.test_anonimo_e_mecanico_sem_acesso_ct005_044` | Retorno HTTP `403 Forbidden` em todas as rotas restritas | **PASSOU** |
| **CT-004** | H01 | Tentativa de login com usuário ou senha incorretos | `Sprint1e2Tests.test_login_credenciais_invalidas_ct004` | Retorno HTTP `400 Bad Request` contendo `"Identificador ou senha inválidos"` sem autenticar sessão | **PASSOU** |
| **CT-005** | H02 | Tentativa de acesso direto via URL por usuário não autenticado (anônimo) | `ControllersCadastrosEOrdensTests.test_anonimo_e_mecanico_sem_acesso_ct005_044` | Retorno HTTP `302 Found` redirecionando para `/login/?next=...` | **PASSOU** |
| **CT-006** | H03, H04 | Cadastro válido de Cliente com CPF formatado e vinculação de 2 Veículos (placa antiga e Mercosul) | `ControllersCadastrosEOrdensTests.test_cliente_e_dois_veiculos_ct006` | CPF salvo normalizado (`11144477735`) e placas salvas como `DEF1234` e `GHI2J34` | **PASSOU** |
| **CT-007** | H03 | Rejeição de CPF inválido (`52998224724`, `11111111111`, `abc`, vazio) | `ControllersCadastrosEOrdensTests.test_cpf_invalido_duplicado_e_retencao_ct007_008_055_069` | Retorno HTTP `400`, erro anexado ao campo `cpf` (`id="id_cpf_error"`) e nenhum registro extra criado | **PASSOU** |
| **CT-008** | H03 | Rejeição de CPF duplicado (enviado com pontuação `529.982.247-25` ou puro `52998224725`) | `ControllersCadastrosEOrdensTests.test_cpf_invalido_duplicado_e_retencao_ct007_008_055_069` | Retorno HTTP `400`, bloqueio de duplicidade e contagem de clientes preservada | **PASSOU** |
| **CT-009** | H04 | Rejeição de placa inválida (`AB123`, `1234567`, `ABC!123`, vazia) | `ControllersCadastrosEOrdensTests.test_placas_invalidas_duplicadas_e_cliente_inexistente_ct009_010_069_070` / `ValidadoresTests.test_placa_invalida` | `ValidationError` / HTTP `400` com destaque de erro no campo `placa` | **PASSOU** |
| **CT-010** | H04 | Rejeição de placa duplicada (`abc1d23` / ` ABC 1D23 `) quando `ABC1D23` já existe | `ControllersCadastrosEOrdensTests.test_placas_invalidas_duplicadas_e_cliente_inexistente_ct009_010_069_070` | Retorno HTTP `400`, retenção do campo `marca` e nenhum veículo duplicado criado | **PASSOU** |
| **CT-014** | H06, H07 | Cadastro de nova Peça (com preço e estoque inicial) e novo Serviço pelo `Dono/Gerente` | `Sprint1e2Tests.test_cadastrar_peca_sucesso_h06` / `test_cadastrar_servico_sucesso_h07` | Registros persistidos no banco (`Amortecedor Dianteiro`, estoque 8; `Alinhamento e Balanceamento 3D`, R$ 120,00) | **PASSOU** |
| **CT-043** | H01 | Logout via POST encerra a sessão ativa | `Sprint1e2Tests.test_login_sucesso_e_logout_invalida_sessao_ct043` | `_auth_user_id` removido de `client.session` e redirecionamento para `/login/` | **PASSOU** |
| **CT-048** | H22 | Validação de campos obrigatórios em branco, e-mail malformado, ano negativo e estoque negativo | `ControllersCadastrosEOrdensTests.test_formularios_validam_email_e_obrigatorios_ct048` / `IntegridadeCatalogoEHistoricoTests.test_estoque_negativo_reprovado_pela_validacao_django` | Formulários reprovados (`is_valid() == False`) e `ValidationError` disparado | **PASSOU** |
| **CT-055** | H22 | Preservação dos dados válidos digitados no formulário quando um campo falha na validação | `ControllersCadastrosEOrdensTests.test_cpf_invalido_duplicado_e_retencao_ct007_008_055_069` | Resposta HTTP `400` mantém o valor `"Nome preservado"` e `"Marca mantida"` nos inputs HTML e aplica a classe `is-invalid` apenas ao campo com erro | **PASSOU** |

---

## 2. Detalhamento Técnico das Evidências de Código

### 2.1 Autenticação e Perfis (`CT-001` a `CT-005`, `CT-043`)
- **Arquivo de Teste:** `core/tests/test_sprint1_sprint2.py` (linhas 62–94) e `core/tests/test_cadastros_e_ordens.py` (linhas 134–158).
- **Verificações realizadas:**
  - Envio de `POST /login/` com credenciais inválidas retorna status `400` e exibe alerta Bootstrap `alert-danger` com o texto `"Identificador ou senha inválidos. Por favor, verifique suas credenciais."`.
  - Requisições sem token CSRF em formulários protegidos (`Client(enforce_csrf_checks=True)`) retornam `403 Forbidden`.
  - Tentativa de acesso de `Mecânico` a `/clientes/`, `/veiculos/`, `/ordens/` retorna `403 Forbidden`.

### 2.2 Cadastro de Clientes e Veículos com Normalização (`CT-006` a `CT-010`, `CT-048`, `CT-055`)
- **Arquivo de Teste:** `core/tests/test_cadastros_e_ordens.py` (linhas 88–131 e 274–291).
- **Verificações realizadas:**
  - Entrada de CPF `111.444.777-35` é validada matematicamente e persistida como `11144477735`.
  - Entradas de placas `'def-1234'` e `' ghi 2j34 '` são normalizadas e persistidas como `'DEF1234'` e `'GHI2J34'`.
  - Quando o CPF falha, o HTML renderizado preserva `value="Nome preservado"` e inclui `class="... is-invalid"` e `<div id="id_cpf_error" class="invalid-feedback d-block">`.

### 2.3 Catálogo de Peças e Serviços (`CT-014`)
- **Arquivo de Teste:** `core/tests/test_sprint1_sprint2.py` (linhas 84–117).
- **Verificações realizadas:**
  - `POST /catalogo/pecas/` com `descricao="Amortecedor Dianteiro"`, `preco="250.00"`, `estoque="8"` cria o registro em `core_peca`.
  - `POST /catalogo/servicos/` com `descricao="Alinhamento e Balanceamento 3D"`, `preco="120.00"` cria o registro em `core_servico`.

---

## 3. Evidência de Configuração de Deploy (H24 e H25)

- **Servidor WSGI (`Procfile`):**
  ```text
  web: gunicorn setup.wsgi --log-file -
  ```
- **Arquivos Estáticos (`setup/settings.py`):**
  ```python
  STATIC_URL = '/static/'
  STATICFILES_DIRS = [BASE_DIR / 'static']
  STATIC_ROOT = BASE_DIR / 'staticfiles'
  STORAGES = {
      "default": {
          "BACKEND": "django.core.files.storage.FileSystemStorage",
      },
      "staticfiles": {
          "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
      },
  }
  ```
- **Comando de Build e Provisionamento Automático no Render:**
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py setup_perfis
  ```

