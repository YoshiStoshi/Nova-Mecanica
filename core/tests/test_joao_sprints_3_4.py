from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Cliente, ItemPeca, ItemServico, OrdemServico, Peca, Servico, Veiculo


class JoaoSprints3e4Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mecanico = User.objects.create_user('joao_mecanico', password='Teste-local-482!')
        cls.mecanico.groups.add(Group.objects.create(name='Mecânico'))
        cls.gerente = User.objects.create_user('joao_gerente', password='Teste-local-482!')
        cls.gerente.groups.add(Group.objects.create(name='Dono/Gerente'))

        cls.cliente = Cliente.objects.create(
            nome='Cliente João', cpf='52998224725', telefone='(16) 99999-9999'
        )
        cls.veiculo = Veiculo.objects.create(
            cliente=cls.cliente, placa='JOA0A01', marca='Fiat', modelo='Argo', ano=2024
        )
        cls.peca_a = Peca.objects.create(nome='Filtro', descricao='Filtro', preco='30.00', estoque=10)
        cls.peca_b = Peca.objects.create(nome='Vela', descricao='Vela', preco='20.00', estoque=10)
        cls.servico_a = Servico.objects.create(nome='Alinhamento', descricao='Alinhamento', preco='80.00')
        cls.servico_b = Servico.objects.create(nome='Balanceamento', descricao='Balanceamento', preco='70.00')

    def nova_os(self, **campos):
        return OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo, **campos)

    def test_h16_painel_exibe_somente_fila_operacional_do_dia(self):
        agora = timezone.now()
        aprovada_hoje = self.nova_os(status='aprovada', aprovada_em=agora)
        execucao_hoje = self.nova_os(status='em_execucao', aprovada_em=agora)
        self.nova_os(status='aprovada', aprovada_em=agora - timedelta(days=1))

        self.client.force_login(self.mecanico)
        response = self.client.get(reverse('core:mecanico_os_dia'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['ordens_fila'].values_list('pk', flat=True)),
            [aprovada_hoje.pk, execucao_hoje.pk],
        )
        self.assertEqual(response.context['total_aprovadas'], 1)
        self.assertEqual(response.context['total_em_execucao'], 1)

    def test_h18_mecanico_conclui_os_com_data_e_hora(self):
        ordem = self.nova_os(status='aprovada', aprovada_em=timezone.now())
        self.client.force_login(self.mecanico)

        response = self.client.post(reverse('core:mecanico_concluir_os', kwargs={'pk': ordem.pk}))

        self.assertRedirects(response, reverse('core:mecanico_os_dia'))
        ordem.refresh_from_db()
        self.assertEqual(ordem.status, 'concluida')
        self.assertIsNotNone(ordem.data_conclusao)
        self.assertEqual(timezone.localdate(ordem.data_conclusao), timezone.localdate())

    def test_h20_h21_rankings_agregam_somente_os_concluidas(self):
        concluida = self.nova_os(
            status='concluida', data_conclusao=timezone.now(), subtotal='290.00', total='290.00'
        )
        pendente = self.nova_os(status='pendente')

        ItemServico.objects.create(
            ordem=concluida, servico=self.servico_a, quantidade=3,
            preco_unitario_historico=Decimal('80.00'),
        )
        ItemServico.objects.create(
            ordem=concluida, servico=self.servico_b, quantidade=3,
            preco_unitario_historico=Decimal('70.00'),
        )
        ItemPeca.objects.create(
            ordem=concluida, peca=self.peca_a, quantidade=2,
            preco_unitario_historico=Decimal('30.00'),
        )
        ItemPeca.objects.create(
            ordem=concluida, peca=self.peca_b, quantidade=4,
            preco_unitario_historico=Decimal('20.00'),
        )
        ItemServico.objects.create(
            ordem=pendente, servico=self.servico_a, quantidade=50,
            preco_unitario_historico=Decimal('80.00'),
        )
        ItemPeca.objects.create(
            ordem=pendente, peca=self.peca_a, quantidade=50,
            preco_unitario_historico=Decimal('30.00'),
        )

        self.client.force_login(self.gerente)
        response = self.client.get(reverse('core:relatorios_dashboard'))

        self.assertEqual(
            [(item['servico__descricao'], item['quantidade_executada']) for item in response.context['ranking_servicos']],
            [('Alinhamento', 3), ('Balanceamento', 3)],
        )
        self.assertEqual(
            [(item['peca__descricao'], item['quantidade_vendida']) for item in response.context['ranking_pecas']],
            [('Vela', 4), ('Filtro', 2)],
        )

    def test_h20_h21_dashboard_exibe_estados_vazios(self):
        self.client.force_login(self.gerente)
        response = self.client.get(reverse('core:relatorios_dashboard'))

        self.assertContains(response, 'Sem serviços executados no período')
        self.assertContains(response, 'Sem peças vendidas no período')
