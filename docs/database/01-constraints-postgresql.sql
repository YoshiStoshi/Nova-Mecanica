-- =============================================================================
-- NOVA MECÂNICA — CONSTRAINTS DE INTEGRIDADE NO POSTGRESQL (SPRINT 1 & SPRINT 2)
-- Autor: Carlos Chen (RA: 2840482421030)
-- =============================================================================
-- Script idempotente para aplicar constraints CHECK nas tabelas geradas pelas
-- migrations do Django (core_peca, core_servico, core_itempeca, core_itemservico).
-- =============================================================================

DO $$
BEGIN
    -- 1. Sprint 1 (H06): Estoque de peças nunca negativo
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_peca_estoque_nao_negativo'
    ) THEN
        ALTER TABLE core_peca
            ADD CONSTRAINT ck_core_peca_estoque_nao_negativo CHECK (estoque >= 0);
    END IF;

    -- 2. Sprint 1 (H06): Preço unitário de peças nunca negativo
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_peca_preco_nao_negativo'
    ) THEN
        ALTER TABLE core_peca
            ADD CONSTRAINT ck_core_peca_preco_nao_negativo CHECK (preco >= 0);
    END IF;

    -- 3. Sprint 1 (H07): Preço de serviços nunca negativo
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_servico_preco_nao_negativo'
    ) THEN
        ALTER TABLE core_servico
            ADD CONSTRAINT ck_core_servico_preco_nao_negativo CHECK (preco >= 0);
    END IF;

    -- 4. Sprint 2 (H13): Quantidade de peças na OS estritamente positiva
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_itempeca_quantidade_positiva'
    ) THEN
        ALTER TABLE core_itempeca
            ADD CONSTRAINT ck_core_itempeca_quantidade_positiva CHECK (quantidade > 0);
    END IF;

    -- 5. Sprint 2 (H14): Quantidade de serviços na OS estritamente positiva
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_itemservico_quantidade_positiva'
    ) THEN
        ALTER TABLE core_itemservico
            ADD CONSTRAINT ck_core_itemservico_quantidade_positiva CHECK (quantidade > 0);
    END IF;

    -- 6. Sprint 2 (H13): Preço unitário histórico congelado da peça não negativo
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_itempeca_preco_historico_nao_negativo'
    ) THEN
        ALTER TABLE core_itempeca
            ADD CONSTRAINT ck_core_itempeca_preco_historico_nao_negativo CHECK (preco_unitario_historico >= 0);
    END IF;

    -- 7. Sprint 2 (H14): Preço unitário histórico congelado do serviço não negativo
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_core_itemservico_preco_historico_nao_negativo'
    ) THEN
        ALTER TABLE core_itemservico
            ADD CONSTRAINT ck_core_itemservico_preco_historico_nao_negativo CHECK (preco_unitario_historico >= 0);
    END IF;
END $$;

