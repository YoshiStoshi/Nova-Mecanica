from decimal import Decimal
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from django.urls import reverse

from core.models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico


class Sprint1e2Tests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.grupo_dono, _ = Group.objects.get_or_create(name='Dono/Gerente')
        cls.grupo_atendente, _ = Group.objects.get_or_create(name='Atendente')
        cls.grupo_mecanico, _ = Group.objects.get_or_create(name='Mecânico')

        core_perms = Permission.objects.filter(content_type__app_label='core')
        cls.grupo_dono.permissions.set(core_perms)

        atendente_perms = Permission.objects.filter(
            content_type__app_label='core',
            codename__in=[
                'view_cliente', 'add_cliente', 'view_veiculo', 'add_veiculo',
                'view_ordemservico', 'add_ordemservico', 'change_ordemservico',
                'view_peca', 'view_servico', 'add_itempeca', 'delete_itempeca',
                'add_itemservico', 'delete_itemservico'
            ]
        )
        cls.grupo_atendente.permissions.set(atendente_perms)

        cls.dono = User.objects.create_user(username='dono_sprint', password='password123')
        cls.dono.groups.add(cls.grupo_dono)

        cls.atendente = User.objects.create_user(username='atendente_sprint', password='password123')
        cls.atendente.groups.add(cls.grupo_atendente)

        cls.mecanico = User.objects.create_user(username='mecanico_sprint', password='password123')
        cls.mecanico.groups.add(cls.grupo_mecanico)

        cls.cliente = Cliente.objects.create(
            nome='Carlos Alberto',
            cpf='12345678901',
            telefone='16988887777',
            email='carlos@teste.com'
        )
        cls.veiculo = Veiculo.objects.create(
            cliente=cls.cliente,
            placa='BRA2E19',
            marca='Toyota',
            modelo='Corolla',
            ano=2021
        )
        cls.peca = Peca.objects.create(
            descricao='Pastilha de Freio Dianteira',
            preco=Decimal('120.00'),
            estoque=10
        )
        cls.servico = Servico.objects.create(
            descricao='Troca de Pastilhas e Fluido',
            preco=Decimal('150.00')
        )

    def test_login_credenciais_invalidas_ct004(self):
        """CT-004: Credenciais inválidas devem exibir erro amigável."""
        response = self.client.post(reverse('core:login'), {
            'username': 'usuario_inexistente',
            'password': 'senha_errada'
        })
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Identificador ou senha inválidos', status_code=400)

    def test_login_sucesso_e_logout_invalida_sessao_ct043(self):
        """CT-043: Login bem sucedido e logout deve invalidar a sessão."""
        response = self.client.post(reverse('core:login'), {
            'username': 'dono_sprint',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('core:home'))
        self.assertIn('_auth_user_id', self.client.session)

        response_logout = self.client.post(reverse('core:logout'))
        self.assertRedirects(response_logout, reverse('core:login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_catalogo_pecas_somente_dono_gerente_h06(self):
        """Apenas Dono/Gerente pode acessar catálogo de peças."""
        self.client.force_login(self.atendente)
        response = self.client.get(reverse('core:pecas'))
        self.assertRedirects(response, reverse('core:home'))

        self.client.force_login(self.dono)
        response = self.client.get(reverse('core:pecas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pastilha de Freio Dianteira')

    def test_cadastrar_peca_sucesso_h06(self):
        """Dono cadastra nova peça com sucesso."""
        self.client.force_login(self.dono)
        response = self.client.post(reverse('core:pecas'), {
            'cadastrar_peca': '1',
            'descricao': 'Amortecedor Dianteiro',
            'preco': '250.00',
            'estoque': '8'
        })
        self.assertRedirects(response, reverse('core:pecas'))
        self.assertTrue(Peca.objects.filter(descricao='Amortecedor Dianteiro', estoque=8).exists())

    def test_cadastrar_servico_sucesso_h07(self):
        """Dono cadastra novo serviço com sucesso."""
        self.client.force_login(self.dono)
        response = self.client.post(reverse('core:servicos'), {
            'cadastrar_servico': '1',
            'descricao': 'Alinhamento e Balanceamento 3D',
            'preco': '120.00'
        })
        self.assertRedirects(response, reverse('core:servicos'))
        self.assertTrue(Servico.objects.filter(descricao='Alinhamento e Balanceamento 3D').exists())

    def test_ajuste_estoque_adicionar_e_definir_h08(self):
        """Dono ajusta saldo de estoque para cima e define saldo fixo."""
        self.client.force_login(self.dono)

        response = self.client.post(reverse('core:peca_ajustar_estoque', kwargs={'pk': self.peca.pk}), {
            'operacao': 'adicionar',
            'quantidade': '5',
            'motivo': 'Compra de reposição'
        })
        self.assertRedirects(response, reverse('core:pecas'))
        self.peca.refresh_from_db()
        self.assertEqual(self.peca.estoque, 15)

        self.client.post(reverse('core:peca_ajustar_estoque', kwargs={'pk': self.peca.pk}), {
            'operacao': 'definir',
            'quantidade': '20',
            'motivo': 'Contagem de inventário'
        })
        self.peca.refresh_from_db()
        self.assertEqual(self.peca.estoque, 20)

    def test_ajuste_estoque_rejeita_saldo_negativo_h08(self):
        """Rejeita redução que gere estoque negativo."""
        self.client.force_login(self.dono)
        response = self.client.post(reverse('core:peca_ajustar_estoque', kwargs={'pk': self.peca.pk}), {
            'operacao': 'remover',
            'quantidade': '15',
            'motivo': 'Tentativa indevida'
        })
        self.assertRedirects(response, reverse('core:pecas'))
        self.peca.refresh_from_db()
        self.assertEqual(self.peca.estoque, 10)

    def test_exclusao_peca_protegida_com_vinculo_os_h09(self):
        """Bloqueia exclusão de peça vinculada a uma OS existente."""
        self.client.force_login(self.dono)

        ordem = OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo, status='pendente')
        ItemPeca.objects.create(ordem=ordem, peca=self.peca, quantidade=1, preco_unitario_historico=Decimal('120.00'))

        response = self.client.post(reverse('core:peca_excluir', kwargs={'pk': self.peca.pk}))
        self.assertRedirects(response, reverse('core:pecas'))
        self.assertTrue(Peca.objects.filter(pk=self.peca.pk).exists())

    def test_exclusao_peca_sem_vinculo_sucesso_h09(self):
        """Permite excluir peça quando ela não possui vínculos com OS."""
        self.client.force_login(self.dono)
        peca_avulsa = Peca.objects.create(descricao='Filtro de Ar Condicionado', preco=Decimal('45.00'), estoque=2)
        response = self.client.post(reverse('core:peca_excluir', kwargs={'pk': peca_avulsa.pk}))
        self.assertRedirects(response, reverse('core:pecas'))
        self.assertFalse(Peca.objects.filter(pk=peca_avulsa.pk).exists())

    def test_tela_orcamento_novo_carrega_com_sucesso_h10(self):
        """Tela de montagem de orçamento carrega dados e catálogos."""
        self.client.force_login(self.atendente)
        response = self.client.get(reverse('core:orcamento_novo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Montagem Dinâmica de Orçamento')
        self.assertContains(response, 'Carlos Alberto')
        self.assertContains(response, 'BRA2E19')

    def test_conversao_orcamento_em_os_sucesso_h11_h12(self):
        """Converte orçamento em Ordem de Serviço com status 'Pendente', congelando preços históricos."""
        self.client.force_login(self.atendente)

        post_data = {
            'cliente': self.cliente.pk,
            'veiculo': self.veiculo.pk,
            'desconto_percentual': '10',
            'observacoes': 'Revisão dos 50.000 km solicitada pelo cliente',
            'pecas_id[]': [str(self.peca.pk)],
            'pecas_qtd[]': ['2'],
            'servicos_id[]': [str(self.servico.pk)],
            'servicos_qtd[]': ['1'],
        }

        response = self.client.post(reverse('core:orcamento_converter'), post_data)

        ordem = OrdemServico.objects.latest('id')
        self.assertRedirects(response, reverse('core:ordem_detalhe', kwargs={'pk': ordem.pk}))

        self.assertEqual(ordem.status, 'pendente')
        self.assertEqual(ordem.desconto_percentual, Decimal('10.00'))
        self.assertEqual(ordem.subtotal, Decimal('390.00'))
        self.assertEqual(ordem.valor_desconto, Decimal('39.00'))
        self.assertEqual(ordem.total, Decimal('351.00'))

        item_peca = ordem.itens_peca.get()
        self.assertEqual(item_peca.preco_unitario_historico, Decimal('120.00'))
        self.assertEqual(item_peca.quantidade, 2)

        item_servico = ordem.itens_servico.get()
        self.assertEqual(item_servico.preco_unitario_historico, Decimal('150.00'))
        self.assertEqual(item_servico.quantidade, 1)

    def test_conversao_orcamento_rejeita_desconto_invalido_h11(self):
        """Rejeita descontos menores que 0 ou maiores que 100%."""
        self.client.force_login(self.atendente)
        post_data = {
            'cliente': self.cliente.pk,
            'veiculo': self.veiculo.pk,
            'desconto_percentual': '120',
            'pecas_id[]': [str(self.peca.pk)],
            'pecas_qtd[]': ['1'],
        }
        response = self.client.post(reverse('core:orcamento_converter'), post_data)
        self.assertRedirects(response, reverse('core:orcamento_novo'))
        self.assertEqual(OrdemServico.objects.count(), 0)

    def test_conversao_orcamento_rejeita_sem_itens_h10(self):
        """Rejeita orçamento que não possui peças nem serviços."""
        self.client.force_login(self.atendente)
        post_data = {
            'cliente': self.cliente.pk,
            'veiculo': self.veiculo.pk,
            'desconto_percentual': '0',
        }
        response = self.client.post(reverse('core:orcamento_converter'), post_data)
        self.assertRedirects(response, reverse('core:orcamento_novo'))
        self.assertEqual(OrdemServico.objects.count(), 0)
