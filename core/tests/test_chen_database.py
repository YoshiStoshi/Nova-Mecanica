from decimal import Decimal
from unittest import skipUnless

from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase

from core.models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico


class IntegridadeCatalogoEHistoricoTests(TestCase):
    """
    Testes de integridade de banco de dados e preservação de preço histórico (Sprints 1 e 2).
    Autor: Carlos Chen (RA: 2840482421030)
    """

    @classmethod
    def setUpTestData(cls):
        cls.cliente = Cliente.objects.create(
            nome="Cliente Teste Banco",
            cpf="52998224725",
            telefone="16991112222",
        )
        cls.veiculo = Veiculo.objects.create(
            cliente=cls.cliente,
            placa="BRA2E19",
            marca="Toyota",
            modelo="Corolla",
            ano=2022,
        )
        cls.peca = Peca.objects.create(
            descricao="Filtro de Óleo Original",
            preco=Decimal("45.00"),
            estoque=10,
        )
        cls.servico = Servico.objects.create(
            descricao="Troca de Óleo e Filtro",
            preco=Decimal("90.00"),
        )

    def test_item_peca_preserva_preco_historico(self):
        """Alterar o preço da peça no catálogo não altera o preço histórico congelado na OS."""
        ordem = OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo)
        item = ItemPeca.objects.create(
            ordem=ordem,
            peca=self.peca,
            quantidade=2,
            preco_unitario_historico=self.peca.preco,
        )

        self.peca.preco = Decimal("75.00")
        self.peca.save(update_fields=["preco", "atualizado_em"])

        item.refresh_from_db()
        self.assertEqual(item.preco_unitario_historico, Decimal("45.00"))
        self.assertEqual(item.subtotal, Decimal("90.00"))

    def test_item_servico_preserva_preco_historico(self):
        """Alterar o preço do serviço no catálogo não altera o preço histórico congelado na OS."""
        ordem = OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo)
        item = ItemServico.objects.create(
            ordem=ordem,
            servico=self.servico,
            quantidade=1,
            preco_unitario_historico=self.servico.preco,
        )

        self.servico.preco = Decimal("140.00")
        self.servico.save(update_fields=["preco", "atualizado_em"])

        item.refresh_from_db()
        self.assertEqual(item.preco_unitario_historico, Decimal("90.00"))
        self.assertEqual(item.subtotal, Decimal("90.00"))

    def test_quantidade_zero_reprovada_pela_validacao_django(self):
        """Validação do modelo recusa quantidade igual a zero em ItemPeca e ItemServico."""
        ordem = OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo)
        item_peca = ItemPeca(
            ordem=ordem,
            peca=self.peca,
            quantidade=0,
            preco_unitario_historico=self.peca.preco,
        )
        with self.assertRaises(ValidationError):
            item_peca.full_clean()

        item_servico = ItemServico(
            ordem=ordem,
            servico=self.servico,
            quantidade=0,
            preco_unitario_historico=self.servico.preco,
        )
        with self.assertRaises(ValidationError):
            item_servico.full_clean()

    def test_estoque_negativo_reprovado_pela_validacao_django(self):
        """Validação do modelo Peca recusa saldo de estoque negativo."""
        peca_invalida = Peca(
            descricao="Peça com Estoque Negativo",
            preco=Decimal("50.00"),
            estoque=-1,
        )
        with self.assertRaises(ValidationError):
            peca_invalida.full_clean()


class ConcorrenciaPostgreSQLChecklistTestes(TestCase):
    """Verifica disponibilidade do PostgreSQL para validação de locks select_for_update."""

    @skipUnless(connection.vendor == "postgresql", "Lock de linha select_for_update requer PostgreSQL.")
    def test_postgresql_ativo_para_select_for_update(self):
        self.assertEqual(connection.vendor, "postgresql")

