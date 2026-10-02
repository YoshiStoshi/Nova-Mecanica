from decimal import Decimal, InvalidOperation
import json

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .calculos import calcular_totais
from .forms import (
    ClienteForm, VeiculoForm, DescontoForm, ItemPecaForm, ItemServicoForm,
    PecaForm, ServicoForm, AjusteEstoqueForm
)
from .forms_login import LoginForm
from .models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico
from .services import incluir_item, remover_item, alterar_desconto, recalcular_ordem


# ==============================================================================
# HELPERS DE PERMISSÃO E PERFIL
# ==============================================================================

def is_dono_ou_gerente(user):
    """Verifica se o usuário pertence ao perfil de Dono/Gerente ou é superusuário."""
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser or
        user.groups.filter(name='Dono/Gerente').exists() or
        user.has_perm('core.add_peca')
    )


def is_atendente_ou_superior(user):
    """Verifica se o usuário é Atendente, Dono/Gerente ou superusuário."""
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser or
        user.groups.filter(name__in=['Dono/Gerente', 'Atendente']).exists() or
        user.has_perm('core.view_cliente')
    )


# ==============================================================================
# DASHBOARD PRINCIPAL & AUTENTICAÇÃO
# ==============================================================================

def home(request):
    """Dashboard principal com métricas operacionais do sistema Nova Mecânica."""
    if not request.user.is_authenticated:
        return redirect('core:login')

    total_clientes = Cliente.objects.count()
    total_veiculos = Veiculo.objects.count()
    ordens_pendentes = OrdemServico.objects.filter(status='pendente').count()
    ordens_em_execucao = OrdemServico.objects.filter(status='em_execucao').count()
    ordens_concluidas = OrdemServico.objects.filter(status='concluida').count()
    total_pecas = Peca.objects.count()
    pecas_baixo_estoque = Peca.objects.filter(estoque__lte=3).count()

    ultimas_ordens = OrdemServico.objects.select_related('cliente', 'veiculo').order_by('-id')[:5]
    pecas_alerta = Peca.objects.filter(estoque__lte=3).order_by('estoque')[:5]

    context = {
        'titulo': 'Dashboard',
        'sistema': 'Nova Mecânica',
        'versao': '1.0.0',
        'total_clientes': total_clientes,
        'total_veiculos': total_veiculos,
        'ordens_pendentes': ordens_pendentes,
        'ordens_em_execucao': ordens_em_execucao,
        'ordens_concluidas': ordens_concluidas,
        'total_pecas': total_pecas,
        'pecas_baixo_estoque': pecas_baixo_estoque,
        'ultimas_ordens': ultimas_ordens,
        'pecas_alerta': pecas_alerta,
    }
    return render(request, 'core/home.html', context)


def login_view(request):
    """Tela de login com feedback visual amigável (H01, H02, CT-004)."""
    if request.user.is_authenticated:
        return redirect('core:home')

    form = LoginForm(request, data=request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if form.is_valid():
            auth_login(request, form.get_user())
            messages.success(request, f'Bem-vindo ao sistema, {request.user.first_name or request.user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next') or reverse('core:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Identificador ou senha inválidos. Por favor, verifique suas credenciais.')

    return render(request, 'usuarios/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
        'titulo': 'Entrar na Oficina',
    }, status=400 if request.method == 'POST' and form.errors else 200)


def logout_view(request):
    """Encerra a sessão do usuário de forma segura (H02, CT-043)."""
    auth_logout(request)
    messages.info(request, 'Você encerrou sua sessão com sucesso.')
    return redirect('core:login')


# ==============================================================================
# CLIENTES & VEÍCULOS
# ==============================================================================

@login_required
@permission_required('core.view_cliente', raise_exception=True)
def clientes(request):
    """Listagem de clientes cadastrados."""
    return render(request, 'core/clientes.html', {'clientes': Cliente.objects.all()})


@login_required
@permission_required('core.view_veiculo', raise_exception=True)
def veiculos(request):
    """Listagem de veículos e seus proprietários."""
    return render(request, 'core/veiculos.html', {'veiculos': Veiculo.objects.select_related('cliente')})


def cadastro(request, form_class, titulo, voltar):
    """Helper genérico de cadastro com preservação de dados e tratamento de duplicidade."""
    form = form_class(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            campo = 'cpf' if form_class is ClienteForm else 'placa'
            form.add_error(campo, 'Já existe um cadastro com este valor.')
        else:
            messages.success(request, 'Cadastro salvo com sucesso.')
            return redirect(voltar)
    return render(request, 'core/cadastro_form.html', {
        'form': form,
        'titulo': titulo,
        'voltar_url': reverse(voltar),
    }, status=400 if request.method == 'POST' and form.errors else 200)


@login_required
@permission_required(('core.add_cliente', 'core.view_cliente'), raise_exception=True)
def cliente_criar(request):
    """Cadastra um novo cliente."""
    return cadastro(request, ClienteForm, 'Cadastrar cliente', 'core:clientes')


@login_required
@permission_required(('core.add_veiculo', 'core.view_veiculo'), raise_exception=True)
def veiculo_criar(request):
    """Cadastra um novo veículo vinculado a um cliente."""
    return cadastro(request, VeiculoForm, 'Cadastrar veículo', 'core:veiculos')


@login_required
def api_veiculos_por_cliente(request, cliente_id):
    """API JSON para carregar veículos de um cliente para autocomplete/dropdown dinâmico."""
    veiculos_qs = Veiculo.objects.filter(cliente_id=cliente_id).values('id', 'placa', 'marca', 'modelo', 'ano')
    return JsonResponse(list(veiculos_qs), safe=False)


# ==============================================================================
# SPRINT 1 (H06, H07) & SPRINT 2 (H08, H09): CATÁLOGO DE PEÇAS E SERVIÇOS
# ==============================================================================

@login_required
def pecas_list_form(request):
    """
    Listagem de peças e formulário/modal de cadastro (H06).
    Exclusivo para Dono/Gerente.
    """
    if not is_dono_ou_gerente(request.user):
        messages.error(request, 'Acesso restrito ao perfil Dono/Gerente.')
        return redirect('core:home')

    form = PecaForm(request.POST if request.method == 'POST' and 'cadastrar_peca' in request.POST else None)

    if request.method == 'POST' and 'cadastrar_peca' in request.POST:
        if form.is_valid():
            nova_peca = form.save()
            messages.success(request, f'Peça "{nova_peca.descricao}" cadastrada com sucesso no catálogo!')
            return redirect('core:pecas')
        else:
            messages.error(request, 'Erro ao salvar a peça. Verifique os campos destacados.')

    termo_busca = request.GET.get('busca', '').strip()
    pecas_qs = Peca.objects.all()
    if termo_busca:
        pecas_qs = pecas_qs.filter(descricao__icontains=termo_busca)

    context = {
        'titulo': 'Catálogo de Peças',
        'pecas': pecas_qs,
        'form': form,
        'ajuste_form': AjusteEstoqueForm(),
        'termo_busca': termo_busca,
        'total_pecas': Peca.objects.count(),
        'total_zeradas': Peca.objects.filter(estoque=0).count(),
        'total_baixas': Peca.objects.filter(estoque__gt=0, estoque__lte=3).count(),
    }
    return render(request, 'catalogo/pecas_list_form.html', context, status=400 if form.errors else 200)


@login_required
@require_POST
def peca_ajustar_estoque(request, pk):
    """
    Ajuste de saldo de estoque pelo Dono/Gerente (H08).
    Rejeita redução que gere saldo negativo no front e no back.
    """
    if not is_dono_ou_gerente(request.user):
        messages.error(request, 'Apenas Dono/Gerente tem permissão para ajustar estoque.')
        return redirect('core:pecas')

    peca = get_object_or_404(Peca, pk=pk)
    form = AjusteEstoqueForm(request.POST)

    if form.is_valid():
        operacao = form.cleaned_data['operacao']
        quantidade = form.cleaned_data['quantidade']
        motivo = form.cleaned_data.get('motivo', '')

        saldo_anterior = peca.estoque
        if operacao == 'adicionar':
            novo_saldo = saldo_anterior + quantidade
        elif operacao == 'remover':
            novo_saldo = saldo_anterior - quantidade
        elif operacao == 'definir':
            novo_saldo = quantidade
        else:
            novo_saldo = saldo_anterior

        if novo_saldo < 0:
            messages.error(
                request,
                f'Ajuste recusado: a redução geraria estoque negativo ({novo_saldo}). O saldo atual é {saldo_anterior}.'
            )
            return redirect('core:pecas')

        peca.estoque = novo_saldo
        peca.save(update_fields=['estoque', 'atualizado_em'])

        info_motivo = f' (Motivo: {motivo})' if motivo else ''
        messages.success(
            request,
            f'Estoque de "{peca.descricao}" ajustado com sucesso de {saldo_anterior} para {novo_saldo} un.{info_motivo}'
        )
    else:
        messages.error(request, 'Dados de ajuste de estoque inválidos.')

    return redirect('core:pecas')


@login_required
@require_POST
def peca_excluir(request, pk):
    """
    Exclusão de peça com proteção visual e de servidor contra vínculo com OS (H09).
    """
    if not is_dono_ou_gerente(request.user):
        messages.error(request, 'Apenas Dono/Gerente tem permissão para excluir itens do catálogo.')
        return redirect('core:pecas')

    peca = get_object_or_404(Peca, pk=pk)

    # Bloqueio caso haja histórico de itens na Ordem de Serviço
    if peca.itens_os.exists():
        messages.error(
            request,
            f'A peça "{peca.descricao}" não pode ser excluída pois está vinculada a ordens de serviço existentes.'
        )
        return redirect('core:pecas')

    nome_peca = peca.descricao
    peca.delete()
    messages.success(request, f'Peça "{nome_peca}" excluída do catálogo com sucesso.')
    return redirect('core:pecas')


@login_required
def servicos_list_form(request):
    """
    Listagem de serviços e formulário de cadastro (H07).
    Exclusivo para Dono/Gerente.
    """
    if not is_dono_ou_gerente(request.user):
        messages.error(request, 'Acesso restrito ao perfil Dono/Gerente.')
        return redirect('core:home')

    form = ServicoForm(request.POST if request.method == 'POST' and 'cadastrar_servico' in request.POST else None)

    if request.method == 'POST' and 'cadastrar_servico' in request.POST:
        if form.is_valid():
            novo_servico = form.save()
            messages.success(request, f'Serviço "{novo_servico.descricao}" cadastrado com sucesso!')
            return redirect('core:servicos')
        else:
            messages.error(request, 'Erro ao salvar o serviço. Verifique os campos.')

    termo_busca = request.GET.get('busca', '').strip()
    servicos_qs = Servico.objects.all()
    if termo_busca:
        servicos_qs = servicos_qs.filter(descricao__icontains=termo_busca)

    context = {
        'titulo': 'Catálogo de Serviços',
        'servicos': servicos_qs,
        'form': form,
        'termo_busca': termo_busca,
        'total_servicos': Servico.objects.count(),
    }
    return render(request, 'catalogo/servicos_list_form.html', context, status=400 if form.errors else 200)


@login_required
@require_POST
def servico_excluir(request, pk):
    """Exclusão protegida de serviço se não houver vínculo com OS."""
    if not is_dono_ou_gerente(request.user):
        messages.error(request, 'Acesso restrito ao perfil Dono/Gerente.')
        return redirect('core:servicos')

    servico = get_object_or_404(Servico, pk=pk)
    if servico.itens_os.exists():
        messages.error(
            request,
            f'O serviço "{servico.descricao}" não pode ser excluído pois está vinculado a ordens de serviço existentes.'
        )
        return redirect('core:servicos')

    nome_servico = servico.descricao
    servico.delete()
    messages.success(request, f'Serviço "{nome_servico}" excluído com sucesso.')
    return redirect('core:servicos')


# ==============================================================================
# SPRINT 2: MONTAGEM DE ORÇAMENTO DINÂMICO & CONVERSÃO EM OS (H10, H11, H12, H13, H14)
# ==============================================================================

@login_required
def orcamento_novo(request):
    """
    Tela de montagem de orçamento dinâmico (H10, H13, H14).
    Permite selecionar Cliente, Veículo e adicionar múltiplas linhas de peças e serviços.
    """
    if not is_atendente_ou_superior(request.user):
        messages.error(request, 'Você não tem permissão para gerar orçamentos.')
        return redirect('core:home')

    clientes_qs = Cliente.objects.all().order_by('nome')
    veiculos_qs = Veiculo.objects.select_related('cliente').order_by('placa')
    pecas_qs = Peca.objects.all().order_by('descricao')
    servicos_qs = Servico.objects.all().order_by('descricao')

    veiculos_data = [
        {
            'id': v.id,
            'cliente_id': v.cliente_id,
            'placa': v.placa,
            'marca': v.marca,
            'modelo': v.modelo,
            'ano': v.ano,
            'descricao': str(v),
        }
        for v in veiculos_qs
    ]

    pecas_data = [
        {
            'id': p.id,
            'descricao': p.descricao,
            'preco': str(p.preco),
            'estoque': p.estoque,
        }
        for p in pecas_qs
    ]

    servicos_data = [
        {
            'id': s.id,
            'descricao': s.descricao,
            'preco': str(s.preco),
        }
        for s in servicos_qs
    ]

    context = {
        'titulo': 'Novo Orçamento',
        'clientes': clientes_qs,
        'veiculos_json': json.dumps(veiculos_data),
        'pecas_json': json.dumps(pecas_data),
        'servicos_json': json.dumps(servicos_data),
        'pecas': pecas_qs,
        'servicos': servicos_qs,
    }
    return render(request, 'orcamentos/orcamento_form.html', context)


@login_required
@require_POST
def orcamento_converter(request):
    """
    Processa a submissão do orçamento e converte diretamente em Ordem de Serviço (H12).
    Cria a Ordem de Serviço com status 'Pendente', congelando os preços unitários históricos.
    """
    if not is_atendente_ou_superior(request.user):
        messages.error(request, 'Você não tem permissão para criar ordens de serviço.')
        return redirect('core:home')

    cliente_id = request.POST.get('cliente')
    veiculo_id = request.POST.get('veiculo')
    desconto_raw = request.POST.get('desconto_percentual', '0').strip() or '0'
    observacoes = request.POST.get('observacoes', '').strip()

    if not cliente_id or not veiculo_id:
        messages.error(request, 'Por favor, selecione o Cliente e o Veículo correspondente.')
        return redirect('core:orcamento_novo')

    cliente = get_object_or_404(Cliente, pk=cliente_id)
    veiculo = get_object_or_404(Veiculo, pk=veiculo_id, cliente=cliente)

    try:
        desconto_val = Decimal(desconto_raw)
        if not (0 <= desconto_val <= 100):
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, 'O desconto deve estar entre 0% e 100%.')
        return redirect('core:orcamento_novo')

    pecas_ids = request.POST.getlist('pecas_id[]')
    pecas_qtds = request.POST.getlist('pecas_qtd[]')
    servicos_ids = request.POST.getlist('servicos_id[]')
    servicos_qtds = request.POST.getlist('servicos_qtd[]')

    if not pecas_ids and not servicos_ids:
        messages.error(request, 'O orçamento deve conter pelo menos uma peça ou um serviço.')
        return redirect('core:orcamento_novo')

    try:
        with transaction.atomic():
            ordem = OrdemServico.objects.create(
                cliente=cliente,
                veiculo=veiculo,
                status='pendente',
                desconto_percentual=desconto_val,
                observacoes=observacoes,
            )

            for p_id, p_qtd in zip(pecas_ids, pecas_qtds):
                if not p_id:
                    continue
                qtd = int(p_qtd)
                if qtd <= 0:
                    raise ValidationError('A quantidade de peças deve ser maior que zero.')
                peca = get_object_or_404(Peca, pk=p_id)
                ItemPeca.objects.create(
                    ordem=ordem,
                    peca=peca,
                    quantidade=qtd,
                    preco_unitario_historico=peca.preco
                )

            for s_id, s_qtd in zip(servicos_ids, servicos_qtds):
                if not s_id:
                    continue
                qtd = int(s_qtd)
                if qtd <= 0:
                    raise ValidationError('A quantidade de serviços deve ser maior que zero.')
                servico = get_object_or_404(Servico, pk=s_id)
                ItemServico.objects.create(
                    ordem=ordem,
                    servico=servico,
                    quantidade=qtd,
                    preco_unitario_historico=servico.preco
                )

            recalcular_ordem(ordem)

    except ValidationError as e:
        messages.error(request, f'Erro de validação: {" ".join(e.messages)}')
        return redirect('core:orcamento_novo')
    except IntegrityError:
        messages.error(request, 'Item duplicado detectado no orçamento. Cada peça ou serviço deve aparecer uma única vez.')
        return redirect('core:orcamento_novo')
    except Exception as e:
        messages.error(request, f'Erro inesperado ao converter orçamento: {str(e)}')
        return redirect('core:orcamento_novo')

    messages.success(
        request,
        f'Orçamento convertido com sucesso! A Ordem de Serviço #{ordem.pk} foi gerada com status Pendente.'
    )
    return redirect('core:ordem_detalhe', pk=ordem.pk)


# ==============================================================================
# ORDENS DE SERVIÇO & ITENS (H13, H14)
# ==============================================================================

@login_required
@permission_required('core.view_ordemservico', raise_exception=True)
def ordens(request):
    """Listagem de todas as ordens de serviço."""
    return render(request, 'core/ordens.html', {'ordens': OrdemServico.objects.select_related('cliente', 'veiculo')})


def render_ordem(request, ordem, status=200, **forms):
    """Helper de renderização da página de detalhes da Ordem de Serviço."""
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
    """Visualização e controle detalhado de uma Ordem de Serviço."""
    ordem = get_object_or_404(OrdemServico.objects.select_related('cliente', 'veiculo'), pk=pk)
    return render_ordem(request, ordem)


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_desconto(request, pk):
    """Aplica ou atualiza o percentual de desconto na OS."""
    ordem = get_object_or_404(OrdemServico, pk=pk)
    form = DescontoForm(request.POST)
    if form.is_valid():
        try:
            alterar_desconto(pk, form.cleaned_data['desconto_percentual'])
        except ValidationError as exc:
            form.add_error(None, ValidationError(exc.messages))
        else:
            messages.success(request, 'Desconto atualizado com sucesso.')
            return redirect('core:ordem_detalhe', pk=pk)
    return render_ordem(request, ordem, status=400, desconto_form=form)


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_item_adicionar(request, pk, tipo):
    """Adiciona um item (peça ou serviço) na OS pendente."""
    if not request.user.has_perm(f'core.add_item{tipo}'):
        raise PermissionDenied
    ordem = get_object_or_404(OrdemServico, pk=pk)
    form_class = ItemPecaForm if tipo == 'peca' else ItemServicoForm
    form = form_class(request.POST, prefix=tipo)
    if form.is_valid():
        try:
            incluir_item(pk, tipo, form.cleaned_data[tipo].pk, form.cleaned_data['quantidade'])
        except ValidationError as exc:
            form.add_error(None, ValidationError(exc.messages))
        except IntegrityError:
            form.add_error(None, 'Este item já está na OS. Remova-o antes de incluí-lo novamente.')
        else:
            messages.success(request, 'Item incluído na OS. O estoque não foi alterado.')
            return redirect('core:ordem_detalhe', pk=pk)
    return render_ordem(request, ordem, status=400, **{f'{tipo}_form': form})


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_item_remover(request, pk, tipo, item_id):
    """Remove um item (peça ou serviço) da OS pendente."""
    if not request.user.has_perm(f'core.delete_item{tipo}'):
        raise PermissionDenied
    ordem = get_object_or_404(OrdemServico, pk=pk)
    try:
        remover_item(pk, tipo, item_id)
    except ValidationError as exc:
        return render_ordem(request, ordem, status=400, erro_operacao=' '.join(exc.messages))
    messages.success(request, 'Item removido e total recalculado.')
    return redirect('core:ordem_detalhe', pk=pk)


@login_required
@permission_required(('core.view_ordemservico', 'core.change_ordemservico'), raise_exception=True)
@require_POST
def ordem_alterar_status(request, pk):
    """Permite transicionar o status da OS (ex: Pendente -> Em Execução -> Concluída)."""
    ordem = get_object_or_404(OrdemServico, pk=pk)
    novo_status = request.POST.get('novo_status')
    if novo_status in dict(OrdemServico.STATUS_CHOICES):
        ordem.status = novo_status
        ordem.save(update_fields=['status', 'atualizado_em'])
        messages.success(request, f'Status da OS #{ordem.pk} alterado para "{ordem.get_status_display()}".')
    else:
        messages.error(request, 'Status informado inválido.')
    return redirect('core:ordem_detalhe', pk=pk)
