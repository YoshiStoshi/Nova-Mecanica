-- =============================================================================
-- NOVA MECÂNICA — SEEDS SINTÉTICOS DE HOMOLOGAÇÃO (SPRINT 1)
-- Autor: Carlos Chen (RA: 2840482421030)
-- =============================================================================
-- ATENÇÃO: Uso exclusivo em ambiente de desenvolvimento e homologação.
-- Inserções idempotentes com WHERE NOT EXISTS sem assumir IDs fixos.
-- =============================================================================

-- 1. Cliente de Homologação
INSERT INTO core_cliente (nome, cpf, telefone, email, criado_em, atualizado_em)
SELECT 'Roberto Almeida (Homologação)', '52998224725', '16991234567', 'roberto.homologacao@exemplo.com', NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM core_cliente WHERE cpf = '52998224725'
);

-- 2. Veículo de Homologação vinculado ao cliente pelo CPF
INSERT INTO core_veiculo (cliente_id, placa, marca, modelo, ano, criado_em, atualizado_em)
SELECT c.id, 'BRA2E19', 'Toyota', 'Corolla XEi 2.0', 2022, NOW(), NOW()
FROM core_cliente c
WHERE c.cpf = '52998224725'
  AND NOT EXISTS (
      SELECT 1 FROM core_veiculo WHERE placa = 'BRA2E19'
  );

-- 3. Peça de Catálogo para Homologação
INSERT INTO core_peca (nome, descricao, preco, estoque, criado_em, atualizado_em)
SELECT 'Kit Pastilha Dianteira Cerâmica', 'Kit Pastilha Dianteira Cerâmica', 185.00, 12, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM core_peca WHERE descricao = 'Kit Pastilha Dianteira Cerâmica'
);

-- 4. Serviço de Catálogo para Homologação
INSERT INTO core_servico (nome, descricao, preco, criado_em, atualizado_em)
SELECT 'Revisão Completa do Sistema de Freios', 'Revisão Completa do Sistema de Freios', 150.00, NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM core_servico WHERE descricao = 'Revisão Completa do Sistema de Freios'
);

