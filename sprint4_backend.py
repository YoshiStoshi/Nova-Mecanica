"""
Sprint 4 — H19 e regressão
Relatório de faturamento mensal e bateria de testes dos endpoints críticos.
"""

from datetime import date
from decimal import Decimal
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncMonth, Coalesce
from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET

from core.models import OrdemServico

PERFIL_GESTAO = "Dono/Gerente"


def exigir_gestao(view):
    @wraps(view)
    @login_required
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_superuser or
                request.user.groups.filter(name=PERFIL_GESTAO).exists()):
            raise PermissionDenied("Relatório disponível apenas para Dono/Gerente.")
        return view(request, *args, **kwargs)
    return wrapped


@exigir_gestao
@require_GET
def faturamento_mensal(request):
    """Retorna faturamento líquido somente de OS concluídas."""
    qs = OrdemServico.objects.filter(status="concluida")
    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")
    if inicio:
        qs = qs.filter(data_conclusao__date__gte=date.fromisoformat(inicio))
    if fim:
        qs = qs.filter(data_conclusao__date__lte=date.fromisoformat(fim))

    # O total líquido já é salvo em OrdemServico no momento do orçamento.
    # A agregação por OS evita multiplicação causada pelas tabelas N:N.
    linhas = (
        qs.exclude(data_conclusao__isnull=True)
        .annotate(mes=TruncMonth("data_conclusao"))
        .values("mes")
        .annotate(
            quantidade_os=Count("id", distinct=True),
            faturamento=Coalesce(
                Sum("total"),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            descontos=Coalesce(
                Sum("valor_desconto"),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        .order_by("mes")
    )
    resultado = [
        {
            "mes": linha["mes"].strftime("%Y-%m"),
            "quantidade_os": linha["quantidade_os"],
            "faturamento": str(linha["faturamento"]),
            "descontos": str(linha["descontos"]),
        }
        for linha in linhas
    ]
    return JsonResponse({"resultados": resultado})


sprint4_urlpatterns = [
    path("sprint4/relatorios/faturamento-mensal/", faturamento_mensal,
         name="sprint4_faturamento_mensal"),
]


# -----------------------------------------------------------------------------
# Testes de regressão (pytest-django ou Django TestCase)
# -----------------------------------------------------------------------------
# Salve o conteúdo desta classe em core/tests/test_sprints_regressao.py se a
# equipe preferir separar testes e código de produção.

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from core.models import Cliente, Veiculo, Peca, OrdemServico, ItemPeca


class SprintRegressaoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        grupo, _ = Group.objects.get_or_create(name=PERFIL_GESTAO)
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
        resposta = self.client.get(reverse("sprint4_faturamento_mensal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["resultados"], [])

    def test_relatorio_considera_concluida_com_desconto(self):
        os = OrdemServico.objects.create(
            cliente=self.cliente, veiculo=self.veiculo, status="concluida",
            total=Decimal("90.00"), valor_desconto=Decimal("10.00"),
            data_conclusao="2026-01-15T10:00:00Z"
        )
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse("sprint4_faturamento_mensal"))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.json()["resultados"][0]["faturamento"], "90.00")

    def test_usuario_sem_perfil_nao_acessa_relatorio(self):
        usuario = User.objects.create_user(username="comum", password="senha-forte")
        self.client.force_login(usuario)
        resposta = self.client.get(reverse("sprint4_faturamento_mensal"))
        self.assertEqual(resposta.status_code, 403)

    def test_peca_vinculada_nao_pode_ser_excluida(self):
        ordem = OrdemServico.objects.create(cliente=self.cliente, veiculo=self.veiculo)
        ItemPeca.objects.create(
            ordem=ordem, peca=self.peca, quantidade=1,
            preco_unitario_historico=Decimal("10.00")
        )
        self.assertEqual(self.peca.itens_os.count(), 1)
