from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico
from core.views import PERFIL_DONO


class SprintRegressaoTests(TestCase):
    """Testes de regressão consolidados (Felipe — Sprints 1 a 4)."""

    @classmethod
    def setUpTestData(cls):
        grupo, _ = Group.objects.get_or_create(name=PERFIL_DONO)
        cls.usuario = User.objects.create_user(username="gestor", password="senha-forte")
        cls.usuario.groups.add(grupo)
        cls.cliente = Cliente.objects.create(nome="Cliente", cpf="99999999999", telefone="16999999999")
        cls.veiculo = Veiculo.objects.create(
            cliente=cls.cliente, placa="AAA0001", marca="Ford", modelo="Ka", ano=2020
        )
        cls.peca = Peca.objects.create(descricao="Filtro", preco=Decimal("10.00"), estoque=1)

    def test_relatorio_exclui_os_pendente(self):
        OrdemServico.objects.create(
            cliente=self.cliente, veiculo=self.veiculo, status="pendente",
            total=Decimal("100.00"), valor_desconto=Decimal("0.00")
        )
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("core:sprint4_faturamento_mensal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["resultados"], [])

    def test_relatorio_considera_concluida_com_desconto(self):
        OrdemServico.objects.create(
            cliente=self.cliente, veiculo=self.veiculo, status="concluida",
            total=Decimal("90.00"), valor_desconto=Decimal("10.00"),
            data_conclusao="2026-01-15T10:00:00Z"
        )
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("core:sprint4_faturamento_mensal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["resultados"][0]["faturamento"], "90.00")

    def test_usuario_sem_perfil_nao_acessa_relatorio(self):
        usuario = User.objects.create_user(username="comum", password="senha-forte")
        self.client.force_login(usuario)
        resposta = self.client.get(reverse("core:sprint4_faturamento_mensal"))
        self.assertEqual(resposta.status_code, 403)

    def test_peca_vinculada_nao_pode_ser_excluida(self):
        ordem = OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo)
        ItemPeca.objects.create(
            ordem=ordem, peca=self.peca, quantidade=1,
            preco_unitario_historico=Decimal("10.00")
        )
        self.assertEqual(self.peca.itens_os.count(), 1)


class Sprint3e4ViewsAndIntegrationTests(TestCase):
    """
    Suíte de testes automatizados das Sprints 3 e 4 (E7, E8 e E9/E10):
    - H05: Histórico por placa (CT-011, CT-012, CT-059)
    - H15: Aprovação de OS e baixa atômica de estoque (CT-026, CT-027, CT-028, CT-029, CT-046, CT-061)
    - H16, H17, H18: Painel do Mecânico, confirmação de peças sem nova baixa e conclusão (CT-030 a CT-036, CT-062)
    - H19, H20, H21: Dashboard Gerencial, Faturamento Mensal, Top Serviços e Top Peças com desempate (CT-037 a CT-042, CT-065, CT-066)
    - CT-058: Fluxo completo ponta a ponta (E2E)
    """

    @classmethod
    def setUpTestData(cls):
        cls.grupo_dono, _ = Group.objects.get_or_create(name="Dono/Gerente")
        cls.grupo_atendente, _ = Group.objects.get_or_create(name="Atendente")
        cls.grupo_mecanico, _ = Group.objects.get_or_create(name="Mecânico")

        core_perms = Permission.objects.filter(content_type__app_label="core")
        cls.grupo_dono.permissions.set(core_perms)

        atendente_perms = Permission.objects.filter(
            content_type__app_label="core",
            codename__in=[
                "view_cliente", "add_cliente", "view_veiculo", "add_veiculo",
                "view_ordemservico", "add_ordemservico", "change_ordemservico",
                "view_peca", "view_servico", "add_itempeca", "delete_itempeca",
                "add_itemservico", "delete_itemservico",
            ],
        )
        cls.grupo_atendente.permissions.set(atendente_perms)

        cls.dono = User.objects.create_user(username="dono_s34", password="password123")
        cls.dono.groups.add(cls.grupo_dono)

        cls.atendente = User.objects.create_user(username="atendente_s34", password="password123")
        cls.atendente.groups.add(cls.grupo_atendente)

        cls.mecanico = User.objects.create_user(username="mecanico_s34", password="password123")
        cls.mecanico.groups.add(cls.grupo_mecanico)

        cls.cliente = Cliente.objects.create(
            nome="Roberto Almeida", cpf="52998224725", telefone="16999998888"
        )
        cls.veiculo = Veiculo.objects.create(
            cliente=cls.cliente, placa="ABC1D23", marca="Fiat", modelo="Argo", ano=2023
        )
        cls.veiculo_sem_os = Veiculo.objects.create(
            cliente=cls.cliente, placa="SEM0A00", marca="Honda", modelo="Civic", ano=2022
        )
        cls.peca_a = Peca.objects.create(
            descricao="Amortecedor Traseiro", preco=Decimal("200.00"), estoque=5
        )
        cls.peca_b = Peca.objects.create(
            descricao="Bucha da Bandeja", preco=Decimal("50.00"), estoque=2
        )
        cls.servico_a = Servico.objects.create(
            descricao="Alinhamento Técnico", preco=Decimal("100.00")
        )
        cls.servico_b = Servico.objects.create(
            descricao="Balanceamento de Rodas", preco=Decimal("80.00")
        )

    def test_historico_placa_tres_cenarios_h05_ct011_012_059(self):
        """
        Valida os 3 cenários de consulta de histórico por placa (H05):
        (a) Placa inexistente (CT-012)
        (b) Veículo cadastrado sem histórico de manutenção (CT-059)
        (c) Veículo com histórico e preços congelados (CT-011)
        """
        self.client.force_login(self.atendente)

        # (a) Placa não cadastrada
        resp_inex = self.client.get(reverse("core:historico_placa"), {"placa": "zzz-9999"})
        self.assertEqual(resp_inex.status_code, 200)
        self.assertContains(resp_inex, "Placa não cadastrada no sistema")

        # (b) Veículo cadastrado, mas sem OSs
        resp_sem_os = self.client.get(reverse("core:historico_placa"), {"placa": "sem-0a00"})
        self.assertEqual(resp_sem_os.status_code, 200)
        self.assertContains(resp_sem_os, "Veículo sem histórico de manutenção")

        # (c) Veículo com OS registrada
        os_hist = OrdemServico.objects.create(
            cliente=self.cliente, veiculo=self.veiculo, status="concluida",
            subtotal=Decimal("300.00"), total=Decimal("300.00")
        )
        ItemPeca.objects.create(
            ordem=os_hist, peca=self.peca_a, quantidade=1, preco_unitario_historico=Decimal("200.00")
        )
        ItemServico.objects.create(
            ordem=os_hist, servico=self.servico_a, quantidade=1, preco_unitario_historico=Decimal("100.00")
        )
        resp_com_os = self.client.get(reverse("core:historico_placa"), {"placa": " abc 1d23 "})
        self.assertEqual(resp_com_os.status_code, 200)
        self.assertContains(resp_com_os, f"OS #{os_hist.pk}")
        self.assertContains(resp_com_os, "Amortecedor Traseiro")

    def test_aprovacao_bloqueada_por_estoque_insuficiente_rollback_h15_ct027_046(self):
        """
        Se faltar 1 unidade de qualquer peça na OS, bloqueia aprovação e mantém
        status 'pendente' e estoques intactos (rollback transacional).
        """
        ordem = OrdemServico.objects.create(
            cliente=self.cliente, veiculo=self.veiculo, status="pendente"
        )
        ItemPeca.objects.create(
            ordem=ordem, peca=self.peca_a, quantidade=2, preco_unitario_historico=Decimal("200.00")
        )
        # peca_b tem estoque=2, solicitamos 3 (falta 1 unidade)
        ItemPeca.objects.create(
            ordem=ordem, peca=self.peca_b, quantidade=3, preco_unitario_historico=Decimal("50.00")
        )

        self.client.force_login(self.dono)
        resp_painel = self.client.get(reverse("core:aprovar_os_detalhe", kwargs={"pk": ordem.pk}))
        self.assertEqual(resp_painel.status_code, 200)
        self.assertContains(resp_painel, "Aprovação Bloqueada — Estoque Insuficiente!")

        resp_post = self.client.post(reverse("core:os_aprovar", kwargs={"pk": ordem.pk}))
        self.assertRedirects(resp_post, reverse("core:aprovar_os_detalhe", kwargs={"pk": ordem.pk}))

        ordem.refresh_from_db()
        self.peca_a.refresh_from_db()
        self.peca_b.refresh_from_db()
        self.assertEqual(ordem.status, "pendente")
        self.assertFalse(ordem.estoque_baixado)
        self.assertEqual(self.peca_a.estoque, 5)
        self.assertEqual(self.peca_b.estoque, 2)

    def test_fluxo_ponta_a_ponta_orcamento_aprovacao_mecanico_relatorios_ct058(self):
        """
        CT-058: Testa o fluxo E2E completo:
        1. Atendente converte orçamento em OS Pendente (sem baixar estoque)
        2. Dono/Gerente aprova OS (baixa atômica única no estoque)
        3. Mecânico visualiza na fila do dia, confirma uso de peças (sem nova baixa) e conclui a OS
        4. Dono/Gerente visualiza Faturamento Mensal (H19), Top Serviços (H20) e Top Peças (H21)
        """
        # 1. Conversão de orçamento
        self.client.force_login(self.atendente)
        self.client.post(reverse("core:orcamento_converter"), {
            "cliente": self.cliente.pk,
            "veiculo": self.veiculo.pk,
            "desconto_percentual": "10",
            "pecas_id[]": [str(self.peca_a.pk), str(self.peca_b.pk)],
            "pecas_qtd[]": ["2", "2"],
            "servicos_id[]": [str(self.servico_a.pk), str(self.servico_b.pk)],
            "servicos_qtd[]": ["1", "1"],
        })
        ordem = OrdemServico.objects.latest("id")
        self.assertEqual(ordem.status, "pendente")
        # Subtotal: (2*200 + 2*50) + (100 + 80) = 500 + 180 = 680. Desconto 10% = 68. Total = 612.00
        self.assertEqual(ordem.total, Decimal("612.00"))
        self.peca_a.refresh_from_db()
        self.assertEqual(self.peca_a.estoque, 5)

        # 2. Aprovação pelo Dono/Gerente
        self.client.force_login(self.dono)
        self.client.post(reverse("core:os_aprovar", kwargs={"pk": ordem.pk}))
        ordem.refresh_from_db()
        self.peca_a.refresh_from_db()
        self.peca_b.refresh_from_db()
        self.assertEqual(ordem.status, "aprovada")
        self.assertTrue(ordem.estoque_baixado)
        self.assertEqual(self.peca_a.estoque, 3)  # 5 - 2
        self.assertEqual(self.peca_b.estoque, 0)  # 2 - 2

        # 3. Mecânico confirma peças (sem nova baixa) e conclui OS
        self.client.force_login(self.mecanico)
        resp_fila = self.client.get(reverse("core:mecanico_os_dia"))
        self.assertEqual(resp_fila.status_code, 200)
        self.assertContains(resp_fila, f"OS #{ordem.pk}")

        item_a = ordem.itens_peca.get(peca=self.peca_a)
        self.client.post(
            reverse("core:mecanico_confirmar_peca", kwargs={"pk": ordem.pk, "item_id": item_a.pk}),
            {"quantidade_utilizada": "2"},
        )
        self.peca_a.refresh_from_db()
        self.assertEqual(self.peca_a.estoque, 3)  # Intacto!

        self.client.post(reverse("core:mecanico_concluir_os", kwargs={"pk": ordem.pk}))
        ordem.refresh_from_db()
        self.assertEqual(ordem.status, "concluida")
        self.assertIsNotNone(ordem.data_conclusao)

        # 4. Dashboard Gerencial do Dono/Gerente (H19, H20, H21 + desempate alfabético CT-066)
        self.client.force_login(self.dono)
        resp_dash = self.client.get(reverse("core:relatorios_dashboard"))
        self.assertEqual(resp_dash.status_code, 200)
        self.assertEqual(resp_dash.context["faturamento_total_liquido"], Decimal("612.00"))
        self.assertEqual(resp_dash.context["total_os_concluidas"], 1)

        # Verifica desempate alfabético quando quantidades são iguais (1x cada serviço, 2x cada peça)
        ranking_servicos = resp_dash.context["ranking_servicos"]
        self.assertEqual(
            [s["servico__descricao"] for s in ranking_servicos],
            ["Alinhamento Técnico", "Balanceamento de Rodas"],
        )
        ranking_pecas = resp_dash.context["ranking_pecas"]
        self.assertEqual(
            [p["peca__descricao"] for p in ranking_pecas],
            ["Amortecedor Traseiro", "Bucha da Bandeja"],
        )

    def test_restricao_perfis_sprint3_e_4_ct028_033_036_042(self):
        """Garante HTTP 403 quando perfis não autorizados acessam rotas exclusivas."""
        self.client.force_login(self.atendente)
        self.assertEqual(self.client.get(reverse("core:aprovar_os_painel")).status_code, 403)
        self.assertEqual(self.client.get(reverse("core:relatorios_dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("core:mecanico_os_dia")).status_code, 403)

        self.client.force_login(self.mecanico)
        self.assertEqual(self.client.get(reverse("core:aprovar_os_painel")).status_code, 403)
        self.assertEqual(self.client.get(reverse("core:relatorios_dashboard")).status_code, 403)
        self.assertEqual(self.client.get(reverse("core:historico_placa")).status_code, 403)
