from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import ClienteForm, VeiculoForm, DescontoForm, ItemPecaForm, ItemServicoForm
from .models import Cliente, Veiculo, OrdemServico
from .services import incluir_item, remover_item, alterar_desconto


@login_required
@permission_required('core.view_cliente', raise_exception=True)
def clientes(request):
    return render(request, 'core/clientes.html', {'clientes': Cliente.objects.all()})


@login_required
@permission_required('core.view_veiculo', raise_exception=True)
def veiculos(request):
    return render(request, 'core/veiculos.html', {'veiculos': Veiculo.objects.select_related('cliente')})


def cadastro(request, form_class, titulo, voltar):
    form = form_class(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            # Trata inclusive dois cadastros concorrentes da mesma identidade.
            campo = 'cpf' if form_class is ClienteForm else 'placa'
            form.add_error(campo, 'Já existe um cadastro com este valor.')
        else:
            messages.success(request, 'Cadastro salvo com sucesso.')
            return redirect(voltar)
    return render(request, 'core/cadastro_form.html', {
        'form': form, 'titulo': titulo, 'voltar_url': reverse(voltar),
    }, status=400 if request.method == 'POST' and form.errors else 200)


@login_required
@permission_required(('core.add_cliente', 'core.view_cliente'), raise_exception=True)
def cliente_criar(request):
    return cadastro(request, ClienteForm, 'Cadastrar cliente', 'core:clientes')


@login_required
@permission_required(('core.add_veiculo', 'core.view_veiculo'), raise_exception=True)
def veiculo_criar(request):
    return cadastro(request, VeiculoForm, 'Cadastrar veículo', 'core:veiculos')


@login_required
@permission_required('core.view_ordemservico', raise_exception=True)
def ordens(request):
    return render(request, 'core/ordens.html', {'ordens': OrdemServico.objects.select_related('cliente', 'veiculo')})


def render_ordem(request, ordem, status=200, **forms):
    context = {
        'ordem': ordem,
        'itens_peca': ordem.itens_peca.select_related('peca'),
        'itens_servico': ordem.itens_servico.select_related('servico'),
        'desconto_form': DescontoForm(instance=ordem),
        'peca_form': ItemPecaForm(prefix='peca'),
        'servico_form': ItemServicoForm(prefix='servico'),
    }
    context.update(forms)
    return render(request, 'core/ordem_detalhe.html', context, status=status)


@login_required
@permission_required('core.view_ordemservico', raise_exception=True)
def ordem_detalhe(request, pk):
    ordem = get_object_or_404(OrdemServico.objects.select_related('cliente', 'veiculo'), pk=pk)
    return render_ordem(request, ordem)


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_desconto(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    form = DescontoForm(request.POST)
    if form.is_valid():
        try:
            alterar_desconto(pk, form.cleaned_data['desconto_percentual'])
        except ValidationError as exc:
            form.add_error(None, ValidationError(exc.messages))
        else:
            messages.success(request, 'Desconto atualizado.')
            return redirect('core:ordem_detalhe', pk=pk)
    return render_ordem(request, ordem, status=400, desconto_form=form)


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_item_adicionar(request, pk, tipo):
    if not request.user.has_perm(f'core.add_item{tipo}'):
        raise PermissionDenied
    ordem = get_object_or_404(OrdemServico, pk=pk)
    form_class = ItemPecaForm if tipo == 'peca' else ItemServicoForm
    form = form_class(request.POST, prefix=tipo)
    if form.is_valid():
        try:
            incluir_item(pk, tipo, form.cleaned_data[tipo].pk, form.cleaned_data['quantidade'])
        except ValidationError as exc:
            # Erros de constraints/modelo são exibidos no formulário do item.
            form.add_error(None, ValidationError(exc.messages))
        except IntegrityError:
            form.add_error(None, 'Este item já está na OS. Remova-o antes de incluí-lo novamente.')
        else:
            messages.success(request, 'Item incluído. O estoque não foi alterado.')
            return redirect('core:ordem_detalhe', pk=pk)
    return render_ordem(request, ordem, status=400, **{f'{tipo}_form': form})


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_item_remover(request, pk, tipo, item_id):
    if not request.user.has_perm(f'core.delete_item{tipo}'):
        raise PermissionDenied
    ordem = get_object_or_404(OrdemServico, pk=pk)
    try:
        remover_item(pk, tipo, item_id)
    except ValidationError as exc:
        return render_ordem(request, ordem, status=400, erro_operacao=' '.join(exc.messages))
    messages.success(request, 'Item removido e total atualizado.')
    return redirect('core:ordem_detalhe', pk=pk)
