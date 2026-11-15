# Ata de Retrospectiva — Sprint 1 (E5)

**Projeto:** Nova Mecânica (Trilha B — FATEC Ribeirão Preto)  
**Data da Reunião:** 22/09/2026  
**Sprint Avaliada:** Sprint 1 (E5) — Período de 21/08/2026 a 22/09/2026  
**Participantes:**
- Rodrigo de Azevedo Junior (RA: 2840482421044)
- João Gabriel Cardoso Martarello (RA: 2840482421028)
- Felipe Delchiaro Malzoni (RA: 2840482421025)
- Carlos Chen (RA: 2840482421030)

---

## 1. O Que Funcionou Bem (Keep Doing)

1. **Padronização Visual desde o Início (`templates/base.html`):**
   - A criação antecipada do layout base pelo Rodrigo com Bootstrap 5.3, tipografia Inter/JetBrains Mono, paleta corporativa azul-marinho e Sidebar responsiva de 220px permitiu que todas as telas criadas pelo grupo (Login, Clientes, Veículos, Peças e Serviços) mantivessem identidade visual coesa.
2. **Separação Clara de Validações e Domínio (`core/validators.py` e `core/forms.py`):**
   - A implementação modular da normalização de CPF e Placa (antiga e Mercosul) evitou duplicação de lógica nas views e garantiu aprovação imediata nos casos de teste `CT-006` a `CT-010`, `CT-048` e `CT-055`.
3. **Configuração Automatizada de Perfis (`setup_perfis`):**
   - O comando customizado `python manage.py setup_perfis` eliminou erros manuais na configuração de permissões dos grupos `Dono/Gerente`, `Atendente` e `Mecânico` entre os ambientes locais dos 4 integrantes e o servidor de produção.
4. **Cobertura de Testes Automatizados e Constraints SQL:**
   - A combinação de testes automatizados (`test_cadastros_e_ordens.py` e `test_sprint1_sprint2.py`) com constraints idempotentes no PostgreSQL (`01-constraints-postgresql.sql`) deu segurança para realizar merges via Pull Request sem quebrar funcionalidades existentes.

---

## 2. O Que Pode Melhorar (Problems / Bottlenecks)

1. **Sincronização de Branches e Padronização de Rotas:**
   - Inicialmente, parte das views e rotas de backend foram desenvolvidas em arquivos separados (`views_joao.py`, `urls_joao.py`, `sprint1_backend.py`), exigindo trabalho de consolidação no momento do merge para unificar tudo em `core/views.py` e `core/urls.py`.
2. **Diferenças de Versão Local do PostgreSQL / Django:**
   - Alguns integrantes encontraram avisos de compatibilidade entre o Django e versões locais do PostgreSQL 14 vs 15+, o que foi resolvido configurando `DatabaseFeatures.minimum_database_version = (14, 0)` em `setup/settings.py` e suportando SQLite para execução rápida da suíte de testes.
3. **Envio de Documentação Fora da Pasta `docs/`:**
   - Alguns arquivos de relatório foram inicialmente subidos na raiz do repositório ou em branches separadas, exigindo revisão para manter estritamente a estrutura `docs/` exigida pela disciplina.

---

## 3. Plano de Ação para a Sprint 2 (Action Items)

| Ação Definida | Responsável | Meta / Prazo |
|---|---|---|
| Unificar todas as rotas principais em `core/urls.py` mantendo os nomes de rota padronizados (`core:<nome>`) | Rodrigo & João | Início da Sprint 2 |
| Implementar o motor de cálculo financeiro em `Decimal` (`ROUND_HALF_UP`) isolado em `core/calculos.py` | João Gabriel | Semana 1 da Sprint 2 |
| Construir a interface dinâmica de orçamento N:N (`orcamento_form.html` + `orcamento.js`) integrada aos endpoints de conversão em OS Pendente | Rodrigo & Felipe | Semana 2 da Sprint 2 |
| Garantir constraints de quantidade positiva e preço histórico congelado nas tabelas `core_itempeca` e `core_itemservico` | Carlos Chen | Semana 2 da Sprint 2 |
| Centralizar 100% dos relatórios e evidências de entrega dentro do diretório `docs/` antes do fechamento da Sprint | Toda a Equipe | Fechamento da Sprint 2 |

---

## 4. Métricas de Fechamento da Sprint 1

- **Histórias Planejadas:** 9 (`H01`, `H02`, `H03`, `H04`, `H06`, `H07`, `H22`, `H24`, `H25`)
- **Histórias Concluídas (Done):** 9 (100% de cumprimento do escopo da Sprint 1)
- **Débitos Técnicos Transferidos para a Sprint 2:** Zero débitos funcionais.

