# Relatório Individual de Contribuição — Sprint 1 (E5)

**Aluno:** Rodrigo de Azevedo Junior  
**RA:** 2840482421044  
**Projeto:** Nova Mecânica  
**Papel no Semestre:** Desenvolvedor Frontend / Configuração Django  
**Período:** 21/08/2026 a 22/09/2026  
**Sprint:** 1 (E5)  

---

## 1. Atividades Realizadas na Sprint

Nesta Sprint 1, atuei como responsável pela estruturação do ambiente base Django, pela arquitetura de templates e layout da interface (UI), configuração do pipeline estático e publicação em nuvem (deploy contínuo):

- **Configuração da Infraestrutura Django (H25):**
  - Criação da estrutura inicial do projeto Django e modularização dos diretórios `templates/` e `static/`.
  - Configuração do pipeline de assets com WhiteNoise no `settings.py` e criação dos arquivos de suporte para produção (`Procfile`, `requirements.txt` e `runtime.txt`).
  - Redação da documentação técnica no `README.md` detalhando pré-requisitos, instalação, execução de migrações e comandos para rodar o projeto localmente.

- **Arquitetura Visual e Template Base:**
  - Desenvolvimento do template mestre `templates/base.html` utilizando Bootstrap 5 e paleta corporativa em tons de azul-marinho (`#0f1f3d`, `#1e3a8a`), conforme o protótipo visual.
  - Implementação da Sidebar fixa (220px) com navegação dinâmica e restrita por perfil de acesso (`request.user.perfil`) para Atendente, Mecânico e Dono/Gerente.
  - Implementação do Header superior contextual com dados do usuário autenticado, badge de cargo e botão de logout via formulário POST protegido por CSRF.
  - Configuração de alertas dinâmicos com `django.contrib.messages` integrados ao Bootstrap para feedback de operações de sucesso e erro.

- **Telas de Autenticação e Perfis (H01, H02):**
  - Construção do template `templates/usuarios/login.html` centralizado, com formulário protegido por token CSRF e exibição amigável de erros de credenciais (CT-004).
  - Roteamento e proteção de views com decoradores `@login_required` para impedir acesso direto por URL a rotas protegidas.

- **Telas do Catálogo de Peças e Serviços (H06, H07, H22):**
  - Desenvolvimento da interface `templates/catalogo/pecas_list_form.html` com listagem de itens e formulário modal para cadastro de novas peças (preço e saldo inicial).
  - Desenvolvimento da interface `templates/catalogo/servicos_list_form.html` para cadastro e listagem de serviços da oficina.
  - Aplicação de classes de feedback visual do Bootstrap (`is-invalid` e `invalid-feedback`) para destacar campos obrigatórios e retenção dos valores válidos preenchidos após erros.

- **Deploy em Produção (H24):**
  - Publicação e homologação da primeira versão estável na nuvem (Render) integrada ao banco de dados PostgreSQL.
  - Verificação de persistência e funcionamento das rotas públicas e autenticadas.

- **Validação Automatizada com Testes (H01, H02, H06, H07):**
  - Implementação de testes automatizados em `core/tests/test_sprint1_sprint2.py` cobrindo o fluxo de login com credenciais válidas/inválidas, logout via POST seguro, bloqueio de rotas sem autenticação, listagem e cadastro de peças/serviços e restrições de permissão por perfil.

---

## 2. Histórias do Backlog Atendidas (E2)

| História | Papel / Contribuição | Status |
|---|---|---|
| **H01** (Autenticação / Login) | Template de login, exibição de erros e fluxo de logout POST | Concluída |
| **H02** (Controle por Perfil) | Sidebar e menus condicionais por perfil de acesso | Concluída |
| **H06** (Catálogo de Peças) | Template de listagem e formulário modal de peças | Concluída |
| **H07** (Catálogo de Serviços) | Template de listagem e formulário modal de serviços | Concluída |
| **H22** (Validações de Formulário) | Estilização de erros e preservação de campos preenchidos | Concluída |
| **H24** (Deploy Público por URL) | Configuração do Render, Gunicorn, WhiteNoise e URL ativa | Concluída |
| **H25** (README Reproduzível) | Redação dos passos de configuração, execução e testes | Concluída |

---

## 3. Evidências Técnicas (PRs e Commits)

- `PR #01` — Setup inicial do projeto Django, WhiteNoise, `Procfile`, `runtime.txt` e `README.md`
- `PR #03` — Estruturação de `base.html`, Sidebar por perfis e estilização com Bootstrap
- `PR #05` — Tela de login (`login.html`), tratamento de mensagens e fluxo de logout via POST
- `PR #08` — Telas de listagem e cadastro de catálogo de peças e serviços
- `PR #11` — Ajustes de deploy em produção no Render e testes de assets estáticos
- `Suíte de Testes` — Testes automatizados em `core/tests/test_sprint1_sprint2.py` executados com 100% de sucesso

---

## 4. Autoavaliação e Lições Aprendidas

A integração dos estilos baseados no protótipo em conjunto com a estrutura padrão de templates do Django permitiu reaproveitar toda a identidade visual sem adicionar complexidade desnecessária de frameworks externos desconectados. O deploy logo no início da Sprint 1 reduziu os riscos de infraestrutura previstos no Documento de Visão e garantiu que o ambiente de produção estivesse disponível continuamente para homologação.
