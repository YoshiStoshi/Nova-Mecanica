# Relatório de Entrega da Sprint 1 (E5) — Documento Capa

**Projeto:** Nova Mecânica — Sistema de Gestão para Oficina Mecânica  
**Disciplina:** Laboratório de Software 3 (Laboratório de Engenharia de Software) — Trilha B  
**Instituição:** FATEC Ribeirão Preto — Curso de Análise e Desenvolvimento de Sistemas (ADS)  
**Sprint:** 1 (E5) — Base Arquitetural, Autenticação por Perfil, Cadastros, Catálogo e Deploy Contínuo  
**Período da Sprint:** 21/08/2026 a 22/09/2026  
**URL de Produção / Homologação (Render):** `https://nova-mecanica.onrender.com`  
**Repositório Oficial:** `https://github.com/YoshiStoshi/Nova-Mecanica`  

---

## 1. Identificação da Equipe Oficial

| Integrante | RA | Papel Principal na Sprint 1 | Relatório Individual |
|---|---|---|---|
| **Rodrigo de Azevedo Junior** | `2840482421044` | Arquitetura Django, Layout Base (`base.html`), Login, Telas de Catálogo, WhiteNoise & Deploy | [sprint-1-contribuicao-rodrigo.md](sprint-1-contribuicao-rodrigo.md) |
| **João Gabriel Cardoso Martarello** | `2840482421028` | Backend de Clientes e Veículos, Validadores de CPF/Placa e Testes Unitários/Integração | [joao-sprint1e2.md](joao-sprint1e2.md) |
| **Felipe Delchiaro Malzoni** | `2840482421025` | Backend de Controle de Acesso por Perfil (`@exigir_perfil`) e Views do Catálogo | [sprint-1-contribuicao-felipe.md](sprint-1-contribuicao-felipe.md) |
| **Carlos Chen** | `2840482421030` | Modelagem Relacional (`models.py`), Constraints PostgreSQL (`CHECK`), Seeds de Homologação e Documentação SQL | [sprint-1-contribuicao-chen.md](sprint-1-contribuicao-chen.md) |

---

## 2. Escopo da Sprint 1: Planejado vs. Entregue

| ID | História de Usuário (Backlog E2) | Prioridade | Planejado | Entregue | Evidência Principal no Repositório |
|---|---|---|---|---|---|
| **H01** | Autenticação de usuários com login e logout seguro via POST | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`login_view`, `logout_view`), `templates/usuarios/login.html` |
| **H02** | Controle de acesso baseado em perfil (Dono/Gerente, Atendente, Mecânico) | Alta (MVP) | Sim | **100% Concluída** | `core/management/commands/setup_perfis.py`, `templates/base.html`, `core/views.py` (`@exigir_perfil`) |
| **H03** | Cadastro e listagem de clientes com validação matemática e normalização de CPF | Alta (MVP) | Sim | **100% Concluída** | `core/validators.py` (`normalizar_cpf`), `core/forms.py` (`ClienteForm`), `templates/core/clientes.html` |
| **H04** | Cadastro e listagem de veículos vinculados a clientes com validação de placa (Antiga/Mercosul) | Alta (MVP) | Sim | **100% Concluída** | `core/validators.py` (`normalizar_placa`), `core/forms.py` (`VeiculoForm`), `templates/core/veiculos.html` |
| **H06** | Cadastro e listagem de peças no catálogo com preço e estoque inicial ($\ge 0$) | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`pecas_list_form`), `templates/catalogo/pecas_list_form.html` |
| **H07** | Cadastro e listagem de serviços de mão de obra no catálogo ($\ge 0$) | Alta (MVP) | Sim | **100% Concluída** | `core/views.py` (`servicos_list_form`), `templates/catalogo/servicos_list_form.html` |
| **H22** | Validação amigável de formulários com destaque de erro (`is-invalid`) e retenção de dados | Média | Sim | **100% Concluída** | `templates/includes/form_fields.html`, `core/forms.py` |
| **H24** | Deploy público acessível por URL com servidor WSGI e arquivos estáticos | Alta (MVP) | Sim | **100% Concluída** | `Procfile`, `runtime.txt`, `setup/settings.py` (WhiteNoise + Gunicorn) |
| **H25** | Documentação `README.md` reproduzível com passo a passo de instalação e execução | Alta (MVP) | Sim | **100% Concluída** | `README.md`, `.env.example`, `requirements.txt` |

---

## 3. Arquitetura e Regras Implementadas na Sprint 1

1. **Segurança e Perfis de Acesso (H01, H02):**
   - Comando `python manage.py setup_perfis` cria e provisiona automaticamente os grupos `Dono/Gerente`, `Atendente` e `Mecânico` com suas permissões granulares.
   - Bloqueio em nível de servidor (`@login_required`, `@permission_required`, `is_dono_ou_gerente`) e adaptação dinâmica da Sidebar fixa de 220px em `templates/base.html`.
   - Logout realizado exclusivamente via requisição `POST` com token CSRF (atendendo ao caso de teste `CT-043`).
2. **Validação de Domínio e Persistência (H03, H04, H06, H07, H22):**
   - CPF validado pelos dígitos verificadores oficiais, normalizado para 11 dígitos numéricos sem máscara no banco e protegido por constraint `UNIQUE`.
   - Placa validada nos formatos `AAA-9999` e Mercosul `AAA9A99`, normalizada para 7 caracteres maiúsculos sem hífen e protegida por constraint `UNIQUE`.
   - Preços e estoques validados no Django (`MinValueValidator`) e no PostgreSQL (`docs/database/01-constraints-postgresql.sql`).
   - Em caso de falha de validação, a view responde com status HTTP `400 Bad Request`, preserva os dados válidos digitados pelo usuário e exibe a mensagem específica no campo com a classe `is-invalid`.
3. **Infraestrutura e Deploy Contínuo (H24, H25):**
   - Pipeline configurado com `gunicorn setup.wsgi:application` no `Procfile` e `CompressedStaticFilesStorage` do `WhiteNoise` em `setup/settings.py`.

---

## 4. Resumo da Execução dos Testes da Sprint 1

As evidências detalhadas encontram-se em [sprint-1-evidencias-teste.md](sprint-1-evidencias-teste.md).

| Caso de Teste | Descrição Resumida | Tipo | Status |
|---|---|---|---|
| **CT-001** | Login com perfil Dono/Gerente e acesso completo ao menu | Funcional / Automatizado | **APROVADO** |
| **CT-002** | Login com perfil Atendente e restrição ao catálogo administrativo | Funcional / Automatizado | **APROVADO** |
| **CT-003** | Login com perfil Mecânico e bloqueio de rotas administrativas/operacionais | Funcional / Automatizado | **APROVADO** |
| **CT-004** | Tentativa de login com credenciais inválidas exibe mensagem amigável | Funcional / Automatizado | **APROVADO** |
| **CT-005** | Bloqueio de acesso anônimo ou perfil sem permissão via URL direta | Segurança / Automatizado | **APROVADO** |
| **CT-006** | Cadastro válido de Cliente e associação de múltiplos Veículos | Funcional / Automatizado | **APROVADO** |
| **CT-007** | Rejeição de CPF inválido (dígitos verificadores incorretos ou sequência repetida) | Domínio / Automatizado | **APROVADO** |
| **CT-008** | Rejeição de CPF duplicado (com ou sem máscara) no cadastro de Cliente | Integridade / Automatizado | **APROVADO** |
| **CT-009** | Rejeição de Placa em formato inválido no cadastro de Veículo | Domínio / Automatizado | **APROVADO** |
| **CT-010** | Rejeição de Placa duplicada no cadastro de Veículo | Integridade / Automatizado | **APROVADO** |
| **CT-014** | Cadastro de Peças e Serviços no catálogo exclusivo pelo Dono/Gerente | Funcional / Automatizado | **APROVADO** |
| **CT-043** | Encerramento seguro de sessão (Logout via POST) e invalidação de sessão | Segurança / Automatizado | **APROVADO** |
| **CT-048** | Rejeição de campos obrigatórios vazios e formatos inválidos (e-mail, ano, estoque) | Validação / Automatizado | **APROVADO** |
| **CT-055** | Retenção dos dados válidos preenchidos no formulário após erro de validação | Usabilidade / Automatizado | **APROVADO** |

---

## 5. Artefatos da Entrega na Pasta `docs/`

- [sprint-1-relatorio-entrega.md](sprint-1-relatorio-entrega.md) — Documento Capa da Sprint 1 (este arquivo)
- [sprint-1-retrospectiva.md](sprint-1-retrospectiva.md) — Ata Oficial de Retrospectiva da Sprint 1
- [sprint-1-evidencias-teste.md](sprint-1-evidencias-teste.md) — Caderno de Evidências de Testes da Sprint 1
- [sprint-1-contribuicao-rodrigo.md](sprint-1-contribuicao-rodrigo.md) — Relatório Individual (Rodrigo de Azevedo Junior)
- [joao-sprint1e2.md](joao-sprint1e2.md) — Relatório Individual (João Gabriel Cardoso Martarello)
- [sprint-1-contribuicao-felipe.md](sprint-1-contribuicao-felipe.md) — Relatório Individual (Felipe Delchiaro Malzoni)
- [sprint-1-contribuicao-chen.md](sprint-1-contribuicao-chen.md) — Relatório Individual (Carlos Chen)

