"""
Sprint 3 — H15 e H17
Aprovação atômica da OS, baixa de estoque e confirmação do uso pelo mecânico.

Migração obrigatória antes da integração:
- OrdemServico.data_conclusao = DateTimeField(null=True, blank=True)
- ItemPeca.quantidade_utilizada = PositiveIntegerField(default=0)
- OrdemServico.estoque_baixado = BooleanField(default=False)
- OrdemServico.aprovada_em = DateTimeField(null=True, blank=True)

Esses campos impedem baixa duplicada e permitem registrar o fechamento da OS.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.models import OrdemServico, ItemPeca, Peca

PERFIL_GESTAO = "Dono/Gerente"
PERFIL_MECANICO = "Mecânico"


def exigir(*perfis):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if not (request.user.is_superuser or
                    request.user.groups.filter(name__in=perfis).exists()):
                raise PermissionDenied("Perfil não autorizado.")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


@exigir(PERFIL_GESTAO)
@require_POST
@transaction.atomic
def aprovar_os(request, pk):
    """Aprova e baixa toda a OS em uma única transação serializável por linhas."""
    ordem = get_object_or_404(
        OrdemServico.objects.select_for_update(), pk=pk
    )
    if ordem.status != "pendente":
        raise ValidationError("Somente OS pendente pode ser aprovada.")
    if getattr(ordem, "estoque_baixado", False):
        raise ValidationError("Esta OS já teve baixa de estoque.")

    itens = list(
        ItemPeca.objects.select_related("peca")
        .filter(ordem=ordem)
        .order_by("peca_id")
    )
    peca_ids = [item.peca_id for item in itens]
    pecas_bloqueadas = {
        p.id: p for p in Peca.objects.select_for_update().filter(id__in=peca_ids)
    }

    insuficientes = []
    for item in itens:
        peca = pecas_bloqueadas[item.peca_id]
        if peca.estoque < item.quantidade:
            insuficientes.append(
                f"{peca.descricao}: disponível {peca.estoque}, necessário {item.quantidade}"
            )
    if insuficientes:
        # Raising dentro de atomic garante rollback e mantém status/estoque intactos.
        raise ValidationError("Estoque insuficiente: " + "; ".join(insuficientes))

    for item in itens:
        peca = pecas_bloqueadas[item.peca_id]
        peca.estoque -= item.quantidade
        peca.save(update_fields=["estoque", "atualizado_em"])

    ordem.status = "aprovada"
    if hasattr(ordem, "estoque_baixado"):
        ordem.estoque_baixado = True
    if hasattr(ordem, "aprovada_em"):
        ordem.aprovada_em = timezone.now()
    update_fields = ["status", "atualizado_em"]
    if hasattr(ordem, "estoque_baixado"):
        update_fields.append("estoque_baixado")
    if hasattr(ordem, "aprovada_em"):
        update_fields.append("aprovada_em")
    ordem.save(update_fields=update_fields)

    return JsonResponse({"os": ordem.pk, "status": ordem.status, "baixa": True})


@exigir(PERFIL_MECANICO)
@require_POST
@transaction.atomic
def confirmar_uso_peca(request, pk, item_id):
    """Registra consumo real sem mexer novamente no estoque."""
    ordem = get_object_or_404(
        OrdemServico.objects.select_for_update(), pk=pk
    )
    if ordem.status not in {"aprovada", "em_execucao"}:
        raise ValidationError("A OS precisa estar aprovada ou em execução.")

    item = get_object_or_404(
        ItemPeca.objects.select_for_update(), pk=item_id, ordem=ordem
    )
    try:
        quantidade_utilizada = int(request.POST.get("quantidade_utilizada", ""))
    except ValueError:
        raise ValidationError("Quantidade utilizada inválida.")
    if quantidade_utilizada < 0 or quantidade_utilizada > item.quantidade:
        raise ValidationError("Uso deve estar entre zero e a quantidade aprovada.")

    # Não há UPDATE em Peca aqui: a baixa ocorreu exclusivamente na aprovação.
    item.quantidade_utilizada = quantidade_utilizada
    item.save(update_fields=["quantidade_utilizada"])
    if ordem.status == "aprovada":
        ordem.status = "em_execucao"
        ordem.save(update_fields=["status", "atualizado_em"])
    return JsonResponse({
        "os": ordem.pk,
        "item": item.pk,
        "quantidade_utilizada": item.quantidade_utilizada,
        "estoque_baixado_novamente": False,
    })


@exigir(PERFIL_MECANICO)
@require_POST
@transaction.atomic
def concluir_os(request, pk):
    """Conclui uma OS em execução e grava o instante de encerramento."""
    ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)
    if ordem.status != "em_execucao":
        raise ValidationError("Somente OS em execução pode ser concluída.")
    ordem.status = "concluida"
    if hasattr(ordem, "data_conclusao"):
        ordem.data_conclusao = timezone.now()
        ordem.save(update_fields=["status", "data_conclusao", "atualizado_em"])
    else:
        ordem.save(update_fields=["status", "atualizado_em"])
    return JsonResponse({"os": ordem.pk, "status": ordem.status})


sprint3_urlpatterns = [
    path("sprint3/ordens/<int:pk>/aprovar/", aprovar_os, name="sprint3_aprovar_os"),
    path("sprint3/ordens/<int:pk>/pecas/<int:item_id>/uso/",
         confirmar_uso_peca, name="sprint3_confirmar_uso"),
    path("sprint3/ordens/<int:pk>/concluir/", concluir_os, name="sprint3_concluir_os"),
]
