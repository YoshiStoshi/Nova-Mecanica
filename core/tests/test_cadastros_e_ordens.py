from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, SimpleTestCase, Client
from unittest import skipUnless
from django.urls import reverse

from core.calculos import calcular_totais
from core import models
from core.validators import normalizar_cpf, normalizar_placa

MODELOS_DISPONIVEIS = all(hasattr(models, nome) for nome in (
    'Cliente', 'Veiculo', 'Peca', 'Servico', 'OrdemServico', 'ItemPeca', 'ItemServico',
))
if MODELOS_DISPONIVEIS:
    from core.forms import ClienteForm, VeiculoForm
    from core.models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico
    from core.services import incluir_item, remover_item, alterar_desconto


class CalculoTests(SimpleTestCase):
    def test_desconto_limites_e_arredondamento_ct020_021_064(self):
        casos = [
            ([(2, '30.00'), (1, '80.00')], '0', '140.00', '0.00', '140.00'),
            ([(1, '1000.00')], '10', '1000.00', '100.00', '900.00'),
            ([(3, '0.10')], '10', '0.30', '0.03', '0.27'),
            ([(1, '1.01')], '10', '1.01', '0.10', '0.91'),
            ([(1, '0.05')], '10', '0.05', '0.00', '0.05'),
            ([(2, '30.00'), (1, '80.00')], '100', '140.00', '140.00', '0.00'),
            ([], '0', '0.00', '0.00', '0.00'),
            ([(1, '0.00')], '0', '0.00', '0.00', '0.00'),
        ]
        for itens, percentual, subtotal, desconto, total in casos:
            with self.subTest(itens=itens, percentual=percentual):
                resultado = calcular_totais(itens, percentual)
                self.assertEqual(resultado, tuple(map(Decimal, (subtotal, desconto, total))))
                self.assertTrue(all(isinstance(valor, Decimal) for valor in resultado))

    def test_descontos_invalidos_ct022(self):
        for valor in ('-1', '101', 'NaN', 'Infinity', 'abc', None, 0.1):
            with self.subTest(valor=valor), self.assertRaises(ValidationError):
                calcular_totais([(1, '10.00')], valor)

    def test_itens_invalidos_ct063(self):
        for item in ((0, '1.00'), (-1, '1.00'), (1.5, '1.00'), (True, '1.00'), (1, '-1'), (1, 'NaN'), (1, 'Infinity'), (1, '0.001'), (1, 0.1)):
            with self.subTest(item=item), self.assertRaises(ValidationError):
                calcular_totais([item])


@skipUnless(MODELOS_DISPONIVEIS, 'Integração pendente: modelos e migrações dos colegas ainda não entregues.')
class ControllersCadastrosEOrdensTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Perfis apenas como fixtures deste teste, sem configurar grupos na aplicação.
        atendimento = {'view_cliente', 'add_cliente', 'view_veiculo', 'add_veiculo',
                       'view_ordemservico', 'change_ordemservico', 'add_itempeca',
                       'delete_itempeca', 'add_itemservico', 'delete_itemservico'}
        for nome, codigos in {'Atendente': atendimento, 'Dono/Gerente': atendimento | {'add_peca'}, 'Mecânico': set()}.items():
            grupo, _ = Group.objects.get_or_create(name=nome)
            grupo.permissions.add(*Permission.objects.filter(content_type__app_label='core', codename__in=codigos))
        cls.atendente = User.objects.create_user('atendente', password='Teste-local-482!')
        cls.atendente.groups.add(Group.objects.get(name='Atendente'))
        cls.mecanico = User.objects.create_user('mecanico', password='Teste-local-482!')
        cls.mecanico.groups.add(Group.objects.get(name='Mecânico'))
        cls.gerente = User.objects.create_user('gerente', password='Teste-local-482!')
        cls.gerente.groups.add(Group.objects.get(name='Dono/Gerente'))
        cls.pessoa = Cliente.objects.create(nome='Cliente sintético', cpf='52998224725', telefone='16900000000')
        cls.veiculo = Veiculo.objects.create(cliente=cls.pessoa, placa='ABC1D23', marca='Marca', modelo='Modelo', ano=2020)
        cls.peca = Peca.objects.create(descricao='Filtro', preco=Decimal('30.00'), estoque=5)
        cls.servico = Servico.objects.create(descricao='Alinhamento', preco=Decimal('80.00'))
        cls.ordem = OrdemServico.objects.create(cliente=cls.pessoa, veiculo=cls.veiculo)

    def setUp(self):
        self.client.force_login(self.atendente)

    def url(self, nome, **kwargs):
        return reverse(f'core:{nome}', kwargs=kwargs)

    def add(self, tipo='peca', quantidade=2, **dados):
        registro = self.peca if tipo == 'peca' else self.servico
        return self.client.post(self.url(f'ordem_{tipo}_adicionar', pk=self.ordem.pk), {
            f'{tipo}-{tipo}': registro.pk, f'{tipo}-quantidade': quantidade, **dados,
        })

    def test_cliente_e_dois_veiculos_ct006(self):
        response = self.client.post(self.url('cliente_criar'), {'nome': 'Novo cliente', 'cpf': '111.444.777-35', 'telefone': '16911111111', 'email': ''})
        self.assertRedirects(response, self.url('clientes'))
        pessoa = Cliente.objects.get(cpf='11144477735')
        for placa in ('def-1234', ' ghi 2j34 '):
            response = self.client.post(self.url('veiculo_criar'), {'cliente': pessoa.pk, 'placa': placa, 'marca': 'Marca', 'modelo': 'Modelo', 'ano': 2024})
            self.assertRedirects(response, self.url('veiculos'))
        self.assertEqual(list(pessoa.veiculos.values_list('placa', flat=True)), ['DEF1234', 'GHI2J34'])

    def test_cpf_invalido_duplicado_e_retencao_ct007_008_055_069(self):
        for cpf in ('529.982.247-25', '52998224725', '52998224724', '11111111111', 'abc', ''):
            with self.subTest(cpf=cpf):
                response = self.client.post(self.url('cliente_criar'), {'nome': 'Nome preservado', 'cpf': cpf, 'telefone': '16911111111'})
                self.assertEqual(response.status_code, 400)
                self.assertIn('cpf', response.context['form'].errors)
                self.assertEqual(len(response.context['form'].errors['cpf']), 1)
                self.assertContains(response, 'id="id_cpf_error"', count=1, status_code=400)
                self.assertContains(response, 'Nome preservado', status_code=400)
                self.assertContains(response, 'is-invalid', status_code=400)
                self.assertEqual(Cliente.objects.count(), 1)

    def test_placas_invalidas_duplicadas_e_cliente_inexistente_ct009_010_069_070(self):
        for placa, cliente in [('abc1d23', self.pessoa.pk), (' ABC 1D23 ', self.pessoa.pk), ('AB123', self.pessoa.pk), ('XYZ9999', 999999)]:
            with self.subTest(placa=placa):
                response = self.client.post(self.url('veiculo_criar'), {'cliente': cliente, 'placa': placa, 'marca': 'Marca mantida', 'modelo': 'Modelo', 'ano': 2024})
                self.assertEqual(response.status_code, 400)
                self.assertContains(response, 'Marca mantida', status_code=400)
                self.assertEqual(Veiculo.objects.count(), 1)

    def test_post_vazio_rejeitado(self):
        for nome in ('cliente_criar', 'veiculo_criar'):
            self.assertEqual(self.client.post(self.url(nome), {}).status_code, 400)

    def test_duplicidade_concorrente_exibe_erro_e_preserva_campos(self):
        with patch('core.forms.ClienteForm.save', side_effect=IntegrityError):
            response = self.client.post(self.url('cliente_criar'), {'nome': 'Nome preservado', 'cpf': '11144477735', 'telefone': '16900000000'})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Nome preservado', status_code=400)
        self.assertIn('cpf', response.context['form'].errors)

    def test_formularios_validam_email_e_obrigatorios_ct048(self):
        self.assertFalse(ClienteForm({'nome': '', 'cpf': '11144477735', 'telefone': '123', 'email': 'invalido'}).is_valid())
        self.assertFalse(VeiculoForm({'cliente': self.pessoa.pk, 'placa': 'DEF1234', 'marca': '', 'modelo': 'Modelo', 'ano': -1}).is_valid())



    def test_anonimo_e_mecanico_sem_acesso_ct005_044(self):
        rotas = [('cliente_criar', {}), ('veiculo_criar', {}), ('clientes', {}), ('veiculos', {}), ('ordens', {}), ('ordem_detalhe', {'pk': self.ordem.pk})]
        for usuario, status in ((None, 302), (self.mecanico, 403)):
            self.client.logout()
            if usuario:
                self.client.force_login(usuario)
            for nome, kwargs in rotas:
                with self.subTest(usuario=usuario, nome=nome):
                    self.assertEqual(self.client.get(self.url(nome, **kwargs)).status_code, status)
            self.assertEqual(self.add().status_code, status)
            self.assertEqual(self.client.post(self.url('ordem_desconto', pk=self.ordem.pk), {'desconto_percentual': 10}).status_code, status)
        self.assertEqual(ItemPeca.objects.count(), 0)

    def test_permissao_de_item_e_verificada_no_servidor(self):
        somente_leitura = User.objects.create_user('leitura')
        somente_leitura.user_permissions.add(*Permission.objects.filter(codename__in=['view_ordemservico', 'change_ordemservico']))
        self.client.force_login(somente_leitura)
        self.assertEqual(self.add().status_code, 403)

    def test_csrf_exigido_em_cadastros_e_itens(self):
        protegido = Client(enforce_csrf_checks=True)
        protegido.force_login(self.atendente)
        for url in (self.url('cliente_criar'), self.url('veiculo_criar'), self.url('ordem_peca_adicionar', pk=self.ordem.pk), self.url('ordem_desconto', pk=self.ordem.pk)):
            self.assertEqual(protegido.post(url, {}).status_code, 403)

    def test_incluir_remover_e_desconto_persistido_ct019_020(self):
        self.assertEqual(self.add().status_code, 302)
        self.assertEqual(self.add('servico', 1).status_code, 302)
        response = self.client.post(self.url('ordem_desconto', pk=self.ordem.pk), {'desconto_percentual': '10.00'})
        self.assertEqual(response.status_code, 302)
        self.ordem.refresh_from_db()
        self.assertEqual((self.ordem.subtotal, self.ordem.valor_desconto, self.ordem.total), (Decimal('140.00'), Decimal('14.00'), Decimal('126.00')))
        for tipo, modelo in [('peca', ItemPeca), ('servico', ItemServico)]:
            item = modelo.objects.get(ordem=self.ordem)
            self.assertEqual(self.client.post(self.url(f'ordem_{tipo}_remover', pk=self.ordem.pk, item_id=item.pk)).status_code, 302)
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.total, Decimal('0.00'))
        self.peca.refresh_from_db()
        self.assertEqual(self.peca.estoque, 5)

    def test_preco_recebido_do_navegador_nao_altera_catalogo_ou_total(self):
        self.assertEqual(self.add(preco_unitario_historico='0.01', total='0', status='aprovada').status_code, 302)
        self.assertEqual(ItemPeca.objects.get().preco_unitario_historico, Decimal('30.00'))
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.total, Decimal('60.00'))
        self.assertEqual(self.ordem.status, 'pendente')

    def test_desconto_invalido_preserva_total_e_formulario_ct022(self):
        incluir_item(self.ordem.pk, 'peca', self.peca.pk, 2)
        for desconto in ('-1', '101', 'NaN', '', '0.001'):
            with self.subTest(desconto=desconto):
                response = self.client.post(self.url('ordem_desconto', pk=self.ordem.pk), {'desconto_percentual': desconto})
                self.assertEqual(response.status_code, 400)
                self.ordem.refresh_from_db()
                self.assertEqual(self.ordem.total, Decimal('60.00'))
                self.assertEqual(self.ordem.desconto_percentual, 0)
                self.assertEqual(response.context['desconto_form']['desconto_percentual'].value(), desconto)

    def test_itens_invalidos_inexistentes_e_duplicados_ct048_063_068(self):
        for tipo in ('peca', 'servico'):
            for quantidade in (0, -1, '1.5', 'abc', ''):
                with self.subTest(tipo=tipo, quantidade=quantidade):
                    self.assertEqual(self.add(tipo, quantidade).status_code, 400)
            self.assertEqual(self.add(tipo, 1, **{f'{tipo}-{tipo}': 99999}).status_code, 400)
            self.assertEqual(self.add(tipo, 1).status_code, 302)
            self.assertEqual(self.add(tipo, 2).status_code, 400)
        self.assertEqual(ItemPeca.objects.get().quantidade, 1)
        self.assertEqual(ItemServico.objects.get().quantidade, 1)

    def test_itens_independentes_entre_ordens_ct050_051(self):
        outra = OrdemServico.objects.create(cliente=self.pessoa, veiculo=self.veiculo)
        for tipo, registro, modelo in [('peca', self.peca, ItemPeca), ('servico', self.servico, ItemServico)]:
            item = incluir_item(self.ordem.pk, tipo, registro.pk, 2)
            incluir_item(outra.pk, tipo, registro.pk, 3)
            remover_item(self.ordem.pk, tipo, item.pk)
            self.assertEqual(modelo.objects.get(ordem=outra).quantidade, 3)
        outra.refresh_from_db()
        self.assertEqual(outra.total, Decimal('330.00'))

    def test_remocao_nao_aceita_item_de_outra_os(self):
        outra = OrdemServico.objects.create(cliente=self.pessoa, veiculo=self.veiculo)
        item = incluir_item(outra.pk, 'peca', self.peca.pk, 1)
        self.assertEqual(self.client.post(self.url('ordem_peca_remover', pk=self.ordem.pk, item_id=item.pk)).status_code, 404)
        self.assertTrue(ItemPeca.objects.filter(pk=item.pk).exists())

    def test_historico_de_preco_e_estoque_preservados_ct054(self):
        incluir_item(self.ordem.pk, 'peca', self.peca.pk, 2)
        incluir_item(self.ordem.pk, 'servico', self.servico.pk, 1)
        Peca.objects.filter(pk=self.peca.pk).update(preco=35)
        Servico.objects.filter(pk=self.servico.pk).update(preco=90)
        alterar_desconto(self.ordem.pk, Decimal('0'))
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.total, Decimal('140.00'))
        self.assertEqual(ItemPeca.objects.get().preco_unitario_historico, Decimal('30.00'))
        self.assertEqual(Peca.objects.get().estoque, 5)

    def test_os_nao_pendente_bloqueia_toda_edicao(self):
        item = incluir_item(self.ordem.pk, 'peca', self.peca.pk, 2)
        for status in ('aprovada', 'em_execucao', 'concluida'):
            OrdemServico.objects.filter(pk=self.ordem.pk).update(status=status)
            self.assertEqual(self.add('servico', 1).status_code, 400)
            self.assertEqual(self.client.post(self.url('ordem_peca_remover', pk=self.ordem.pk, item_id=item.pk)).status_code, 400)
            self.assertEqual(self.client.post(self.url('ordem_desconto', pk=self.ordem.pk), {'desconto_percentual': 10}).status_code, 400)
        self.assertTrue(ItemPeca.objects.filter(pk=item.pk).exists())
        self.ordem.refresh_from_db()
        self.assertEqual(self.ordem.total, Decimal('60.00'))

    def test_get_nao_altera_itens_ou_desconto(self):
        item = incluir_item(self.ordem.pk, 'peca', self.peca.pk, 1)
        for url in (self.url('ordem_peca_adicionar', pk=self.ordem.pk), self.url('ordem_peca_remover', pk=self.ordem.pk, item_id=item.pk), self.url('ordem_desconto', pk=self.ordem.pk)):
            self.assertEqual(self.client.get(url).status_code, 405)

    def test_falha_no_calculo_desfaz_inclusao_e_remocao(self):
        with patch('core.services.recalcular_ordem', side_effect=ValidationError('Falha de teste')):
            with self.assertRaises(ValidationError):
                incluir_item(self.ordem.pk, 'peca', self.peca.pk, 1)
        self.assertEqual(ItemPeca.objects.count(), 0)
        item = incluir_item(self.ordem.pk, 'peca', self.peca.pk, 1)
        with patch('core.services.recalcular_ordem', side_effect=ValidationError('Falha de teste')):
            with self.assertRaises(ValidationError):
                remover_item(self.ordem.pk, 'peca', item.pk)
        self.assertTrue(ItemPeca.objects.filter(pk=item.pk).exists())

    def test_total_acima_do_limite_e_recusado_sem_salvar_item(self):
        Peca.objects.filter(pk=self.peca.pk).update(preco=Decimal('99999999.99'))
        self.assertEqual(self.add(quantidade=2147483647).status_code, 400)
        self.assertEqual(ItemPeca.objects.count(), 0)



    def test_paginas_e_perfis(self):
        for usuario in (self.atendente, self.gerente):
            self.client.force_login(usuario)
            for nome in ('home', 'clientes', 'veiculos', 'ordens', 'cliente_criar', 'veiculo_criar'):
                self.assertEqual(self.client.get(self.url(nome)).status_code, 200)
            self.assertEqual(self.client.get(self.url('ordem_detalhe', pk=self.ordem.pk)).status_code, 200)
        self.assertFalse(self.atendente.has_perm('core.add_peca'))
        self.assertTrue(self.gerente.has_perm('core.add_peca'))


class ValidadoresTests(SimpleTestCase):
    def test_cpf_normalizado(self):
        self.assertEqual(normalizar_cpf('529.982.247-25'), '52998224725')
        self.assertEqual(normalizar_cpf('52998224725'), '52998224725')

    def test_cpf_invalido(self):
        for cpf in ('11111111111', '52998224724', 'abc', ''):
            with self.subTest(cpf=cpf), self.assertRaises(ValidationError):
                normalizar_cpf(cpf)

    def test_placas_normalizadas(self):
        self.assertEqual(normalizar_placa(' abc-1234 '), 'ABC1234')
        self.assertEqual(normalizar_placa(' abc 1d23 '), 'ABC1D23')

    def test_placa_invalida(self):
        for placa in ('AB123', '1234567', '', 'ABC!123'):
            with self.subTest(placa=placa), self.assertRaises(ValidationError):
                normalizar_placa(placa)
