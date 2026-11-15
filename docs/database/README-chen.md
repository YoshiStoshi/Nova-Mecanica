# Documentação de Banco de Dados e Integridade — Nova Mecânica

**Responsável:** Carlos Chen (RA: 2840482421030)  
**Banco Homologado:** PostgreSQL 15+ (Desenvolvimento / Render) e SQLite (Testes Rápidos)

---

## 1. Ordem Recomendada de Execução no PostgreSQL

As migrations do Django (`core/migrations/`) são a fonte primária da estrutura de tabelas. Os scripts SQL deste diretório adicionam camadas extras de integridade relacional diretamente no banco PostgreSQL:

1. **Executar as migrations do Django:**
   ```bash
   python manage.py migrate
   python manage.py setup_perfis
   ```
2. **Conferir dados existentes** (garantir que não há registros legados violando preços ou estoques negativos).
3. **Aplicar as constraints de integridade (Sprint 1 e Sprint 2):**
   ```bash
   psql -U postgres -d NovaMecDB -f docs/database/01-constraints-postgresql.sql
   ```
4. **Popular dados sintéticos de homologação (apenas em dev/staging, NUNCA em produção):**
   ```bash
   psql -U postgres -d NovaMecDB -f docs/database/02-seeds-homologacao.sql
   ```
5. **Executar a suíte de testes de banco e integridade:**
   ```bash
   python manage.py test core.tests.test_chen_database
   ```

---

## 2. Regras de Integridade Implementadas

- **Catálogo (`core_peca`, `core_servico`):**
  - `ck_core_peca_estoque_nao_negativo`: impede saldo `estoque < 0`.
  - `ck_core_peca_preco_nao_negativo` e `ck_core_servico_preco_nao_negativo`: impedem preços negativos.
- **Tabelas Associativas N:N (`core_itempeca`, `core_itemservico`):**
  - `ck_core_itempeca_quantidade_positiva` e `ck_core_itemservico_quantidade_positiva`: exigem `quantidade > 0`.
  - `ck_core_itempeca_preco_historico_nao_negativo` e `ck_core_itemservico_preco_historico_nao_negativo`: garantem `preco_unitario_historico >= 0`.
  - `ON DELETE PROTECT` na FK para `Peca` e `Servico`: impede exclusão de itens de catálogo vinculados a qualquer Ordem de Serviço (H09).
  - `ON DELETE CASCADE` na FK para `OrdemServico`: remove os itens associados caso uma OS de teste seja removida.

---

## 3. Checklist de Concorrência para Baixa de Estoque (H15)

- A baixa de estoque ocorre **exclusivamente na aprovação da OS pelo Dono/Gerente (H15)**.
- Para evitar condição de corrida (*race condition*) quando duas aprovações concorrentes disputam a mesma peça, a operação deve obrigatoriamente utilizar `transaction.atomic()` combinada com `Peca.objects.select_for_update()` em PostgreSQL.

