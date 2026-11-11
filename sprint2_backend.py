"""
Sprint 2 — H08, H09 e H12
Conversão de orçamento em OS e endpoints de estoque.

O projeto atual já possui o fluxo de orçamento em core.views. As funções abaixo
podem ser usadas como camada de serviço/API para manter as regras no backend.
"""

from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import path
from django.views.decorators.http import require_POST

from core.models import (
    Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico,
)
from core.services import recalcular_ordem

PERFIL_DONO = "Dono/Gerente"
PERFIS_ORCAMENTO = ("Dono/Gerente", "Atendente")


def tem_perfil(user, perfis):
    return bool(user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__in=perfis).exists()
    ))


def perfil_necessario(*perfis):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if not tem_perfil(request.user, perfis):
                raise PermissionDenied("Perfil não autorizado.")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def _decimal(valor, nome):
    try:
        resultado = Decimal(str(valor or "0"))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f"{nome} inválido.")
    return resultado


@perfil_necessario(*PERFIS_ORCAMENTO)
@require_POST
def converter_orcamento_em_os(request):
    """Cria uma OS pendente, congelando os preços do catálogo sem baixar estoque."""
    cliente = get_object_or_404(Cliente, pk=request.POST.get("cliente"))
    veiculo = get_object_or_404(Veiculo, pk=request.POST.get("veiculo"), cliente=cliente)
    desconto = _decimal(request.POST.get("desconto_percentual", 0), "Desconto")
    if not Decimal("0") <= desconto <= Decimal("100"):
        raise ValidationError("O desconto deve estar entre 0 e 100%.")

    pecas = request.POST.getlist("pecas_id[]")
    qtd_pecas = request.POST.getlist("pecas_qtd[]")
    servicos = request.POST.getlist("servicos_id[]")
    qtd_servicos = request.POST.getlist("servicos_qtd[]")
    if not pecas and not servicos:
        raise ValidationError("A OS deve conter ao menos um item.")

    try:
        with transaction.atomic():
            ordem = OrdemServico.objects.create(
                cliente=cliente, veiculo=veiculo, status="pendente",
                desconto_percentual=desconto,
                observacoes=request.POST.get("observacoes", "").strip(),
            )
            for pk, raw_qtd in zip(pecas, qtd_pecas):
                if not pk:
                    continue
                peca = Peca.objects.get(pk=pk)
                qtd = int(raw_qtd)
                if qtd <= 0:
                    raise ValidationError("A quantidade da peça deve ser positiva.")
                ItemPeca.objects.create(
                    ordem=ordem, peca=peca, quantidade=qtd,
                    preco_unitario_historico=peca.preco,
                )
            for pk, raw_qtd in zip(servicos, qtd_servicos):
                if not pk:
                    continue
                servico = Servico.objects.get(pk=pk)
                qtd = int(raw_qtd)
                if qtd <= 0:
                    raise ValidationError("A quantidade do serviço deve ser positiva.")
                ItemServico.objects.create(
                    ordem=ordem, servico=servico, quantidade=qtd,
                    preco_unitario_historico=servico.preco,
                )
            recalcular_ordem(ordem)
    except (Peca.DoesNotExist, Servico.DoesNotExist, ValueError, IntegrityError) as exc:
        raise ValidationError(f"Itens inválidos ou duplicados: {exc}")

    return JsonResponse({
        "id": ordem.pk,
        "status": ordem.status,
        "total": str(ordem.total),
        "estoque_baixado": False,
    }, status=201)


@perfil_necessario(PERFIL_DONO)
@require_POST
def ajustar_estoque_api(request, pk):
    """Ajusta estoque com lock de linha e bloqueio de saldo negativo."""
    operacao = request.POST.get("operacao")
    try:
        quantidade = int(request.POST.get("quantidade", ""))
    except ValueError:
        raise ValidationError("Quantidade deve ser um número inteiro.")
    if quantidade < 0 or operacao not in {"adicionar", "remover", "definir"}:
        raise ValidationError("Operação ou quantidade inválida.")

    with transaction.atomic():
        peca = Peca.objects.select_for_update().get(pk=pk)
        if operacao == "adicionar":
            novo_saldo = peca.estoque + quantidade
        elif operacao == "remover":
            novo_saldo = peca.estoque - quantidade
        else:
            novo_saldo = quantidade
        if novo_saldo < 0:
            raise ValidationError("Ajuste recusado: o estoque não pode ficar negativo.")
        anterior = peca.estoque
        peca.estoque = novo_saldo
        peca.save(update_fields=["estoque", "atualizado_em"])

    return JsonResponse({"peca": peca.pk, "anterior": anterior, "estoque": novo_saldo})


@perfil_necessario(PERFIL_DONO)
@require_POST
def excluir_peca_protegida_api(request, pk):
    """Exclui somente peça sem vínculo histórico com item de OS."""
    with transaction.atomic():
        peca = Peca.objects.select_for_update().get(pk=pk)
        if peca.itens_os.exists():
            raise ValidationError("Peça vinculada a OS não pode ser excluída.")
        peca.delete()
    return JsonResponse({"excluida": True})


sprint2_urlpatterns = [
    path("sprint2/orcamentos/converter/", converter_orcamento_em_os,
         name="sprint2_converter_orcamento"),
    path("sprint2/pecas/<int:pk>/estoque/", ajustar_estoque_api,
         name="sprint2_ajustar_estoque"),
    path("sprint2/pecas/<int:pk>/excluir/", excluir_peca_protegida_api,
         name="sprint2_excluir_peca"),
]
