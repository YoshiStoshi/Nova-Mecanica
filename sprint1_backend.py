"""
Sprint 1 — H02, H06 e H07
Backend Django de autenticação por perfil e catálogos.

Integração sugerida:
    from sprint1_backend import sprint1_urlpatterns
    urlpatterns += sprint1_urlpatterns

O projeto atual já possui views equivalentes em core.views. Este arquivo concentra
uma versão reutilizável, com decorators explícitos, para a entrega da Sprint 1.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path
from django.views.decorators.http import require_http_methods, require_POST

from core.forms import PecaForm, ServicoForm
from core.models import Peca, Servico


PERFIL_DONO = "Dono/Gerente"
PERFIL_ATENDENTE = "Atendente"
PERFIL_MECANICO = "Mecânico"


def usuario_tem_perfil(user, *perfis):
    """Retorna True para superusuário ou usuário pertencente a um dos grupos."""
    return bool(
        user.is_authenticated
        and (user.is_superuser or user.groups.filter(name__in=perfis).exists())
    )


def exigir_perfil(*perfis):
    """Decorator para bloquear também requisições diretas à URL."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if not usuario_tem_perfil(request.user, *perfis):
                raise PermissionDenied("Usuário sem permissão para esta operação.")
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


@exigir_perfil(PERFIL_DONO)
@require_http_methods(["GET", "POST"])
def catalogo_pecas(request):
    """Lista e cadastra peças. Exclusivo para Dono/Gerente."""
    form = PecaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            peca = form.save()
        messages.success(request, f'Peça "{peca.descricao}" cadastrada.')
        return redirect("core:sprint1_pecas")

    busca = request.GET.get("busca", "").strip()
    pecas = Peca.objects.all()
    if busca:
        pecas = pecas.filter(descricao__icontains=busca)
    return render(request, "catalogo/pecas_list_form.html", {
        "titulo": "Catálogo de Peças",
        "pecas": pecas,
        "form": form,
        "termo_busca": busca,
    })


@exigir_perfil(PERFIL_DONO)
@require_http_methods(["GET", "POST"])
def catalogo_servicos(request):
    """Lista e cadastra serviços. Exclusivo para Dono/Gerente."""
    form = ServicoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            servico = form.save()
        messages.success(request, f'Serviço "{servico.descricao}" cadastrado.')
        return redirect("core:sprint1_servicos")

    busca = request.GET.get("busca", "").strip()
    servicos = Servico.objects.all()
    if busca:
        servicos = servicos.filter(descricao__icontains=busca)
    return render(request, "catalogo/servicos_list_form.html", {
        "titulo": "Catálogo de Serviços",
        "servicos": servicos,
        "form": form,
        "termo_busca": busca,
    })


@exigir_perfil(PERFIL_DONO)
@require_POST
def excluir_peca_sem_vinculo(request, pk):
    """Exclui peça apenas quando não há ItemPeca apontando para ela."""
    peca = get_object_or_404(Peca, pk=pk)
    if peca.itens_os.exists():
        messages.error(request, "Peças vinculadas a OS não podem ser excluídas.")
    else:
        peca.delete()
        messages.success(request, "Peça excluída do catálogo.")
    return redirect("core:sprint1_pecas")


@exigir_perfil(PERFIL_DONO)
@require_POST
def excluir_servico_sem_vinculo(request, pk):
    """Exclui serviço apenas quando não há ItemServico apontando para ele."""
    servico = get_object_or_404(Servico, pk=pk)
    if servico.itens_os.exists():
        messages.error(request, "Serviços vinculados a OS não podem ser excluídos.")
    else:
        servico.delete()
        messages.success(request, "Serviço excluído do catálogo.")
    return redirect("core:sprint1_servicos")


sprint1_urlpatterns = [
    path("sprint1/catalogo/pecas/", catalogo_pecas, name="sprint1_pecas"),
    path("sprint1/catalogo/servicos/", catalogo_servicos, name="sprint1_servicos"),
    path("sprint1/catalogo/pecas/<int:pk>/excluir/", excluir_peca_sem_vinculo,
         name="sprint1_excluir_peca"),
    path("sprint1/catalogo/servicos/<int:pk>/excluir/", excluir_servico_sem_vinculo,
         name="sprint1_excluir_servico"),
]
