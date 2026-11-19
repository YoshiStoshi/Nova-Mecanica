from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps
import json
import re

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction, IntegrityError
from django.db.models import Sum, Count, F, DecimalField
from django.db.models.functions import TruncMonth, Coalesce
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .calculos import calcular_totais
from .forms import (
    ClienteForm, VeiculoForm, DescontoForm, ItemPecaForm, ItemServicoForm,
    PecaForm, ServicoForm, AjusteEstoqueForm
)
from .forms_login import LoginForm
from .models import Cliente, Veiculo, Peca, Servico, OrdemServico, ItemPeca, ItemServico
from .services import incluir_item, remover_item, alterar_desconto, recalcular_ordem


# ==============================================================================
# HELPERS E DECORATORS UNIFICADOS DE PERMISSÃO E PERFIL (H01, H02)
# ==============================================================================

PERFIL_DONO = 'Dono/Gerente'
PERFIL_ATENDENTE = 'Atendente'
PERFIL_MECANICO = 'Mecânico'
PERFIS_ORCAMENTO = (PERFIL_DONO, PERFIL_ATENDENTE)


def usuario_tem_perfil(user, *perfis):
    """Retorna True para superusuário ou usuário pertencente a um dos grupos informados."""
    return bool(
        user.is_authenticated
        and (user.is_superuser or user.groups.filter(name__in=perfis).exists())
    )


def exigir_perfil(*perfis):
    """Decorator unificado para bloquear requisições diretas à URL quando o usuário não tem o perfil."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if not usuario_tem_perfil(request.user, *perfis):
                raise PermissionDenied('Usuário sem permissão para esta operação.')
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def is_dono_ou_gerente(user):
    """Verifica se o usuário pertence ao perfil de Dono/Gerente ou é superusuário."""
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser or
        user.groups.filter(name=PERFIL_DONO).exists() or
        user.has_perm('core.add_peca')
    )


def is_atendente_ou_superior(user):
    """Verifica se o usuário é Atendente, Dono/Gerente ou superusuário."""
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser or
        user.groups.filter(name__in=[PERFIL_DONO, PERFIL_ATENDENTE]).exists() or
        user.has_perm('core.view_cliente')
    )


def is_mecanico_ou_gerente(user):
    """Verifica se o usuário pertence ao perfil Mecânico, Dono/Gerente ou é superusuário."""
    if not user.is_authenticated:
        return False
    return (
        user.is_superuser or
        user.groups.filter(name__in=[PERFIL_MECANICO, PERFIL_DONO]).exists()
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
        update_fields = ['status', 'atualizado_em']
        if novo_status == 'concluida' and not ordem.data_conclusao:
            ordem.data_conclusao = timezone.now()
            update_fields.append('data_conclusao')
        ordem.save(update_fields=update_fields)
        messages.success(request, f'Status da OS #{ordem.pk} alterado para "{ordem.get_status_display()}".')
    else:
        messages.error(request, 'Status informado inválido.')
    return redirect('core:ordem_detalhe', pk=pk)


# ==============================================================================
# SPRINT 3 (E7): APROVAÇÃO ATÔMICA DE OS, HISTÓRICO POR PLACA E PAINEL MECÂNICO
# ==============================================================================

@login_required
def aprovar_os_painel(request, pk=None):
    """
    Painel de Aprovação de Ordens de Serviço Pendentes (H15).
    Exclusivo para Dono/Gerente. Compara a quantidade solicitada de cada peça
    com o saldo atual em estoque e bloqueia visualmente a aprovação se faltar saldo.
    """
    if not is_dono_ou_gerente(request.user):
        raise PermissionDenied('Apenas Dono/Gerente tem permissão para aprovar Ordens de Serviço.')

    ordens_pendentes_qs = (
        OrdemServico.objects.filter(status='pendente')
        .select_related('cliente', 'veiculo')
        .prefetch_related('itens_peca__peca', 'itens_servico__servico')
        .order_by('-id')
    )

    ordens_analisadas = []
    ordem_selecionada = None

    for os_obj in ordens_pendentes_qs:
        itens_peca_info = []
        insuficientes = []
        for item in os_obj.itens_peca.all():
            estoque_atual = item.peca.estoque
            suficiente = estoque_atual >= item.quantidade
            faltante = max(0, item.quantidade - estoque_atual)
            if not suficiente:
                insuficientes.append({
                    'descricao': item.peca.descricao,
                    'solicitado': item.quantidade,
                    'disponivel': estoque_atual,
                    'faltante': faltante,
                })
            itens_peca_info.append({
                'item': item,
                'estoque_atual': estoque_atual,
                'suficiente': suficiente,
                'faltante': faltante,
            })

        apta = len(insuficientes) == 0
        os_dict = {
            'ordem': os_obj,
            'itens_peca_info': itens_peca_info,
            'itens_servico': list(os_obj.itens_servico.all()),
            'insuficientes': insuficientes,
            'apta_aprovacao': apta,
        }
        ordens_analisadas.append(os_dict)
        if pk and os_obj.pk == pk:
            ordem_selecionada = os_dict

    if not ordem_selecionada and ordens_analisadas:
        ordem_selecionada = ordens_analisadas[0]

    context = {
        'titulo': 'Aprovação de Ordens de Serviço',
        'ordens_analisadas': ordens_analisadas,
        'ordem_selecionada': ordem_selecionada,
        'total_pendentes': len(ordens_analisadas),
        'total_aptas': sum(1 for o in ordens_analisadas if o['apta_aprovacao']),
        'total_bloqueadas': sum(1 for o in ordens_analisadas if not o['apta_aprovacao']),
    }
    return render(request, 'os/aprovar_os.html', context)


@login_required
@require_POST
def aprovar_os_confirmar(request, pk):
    """
    Aprova a OS e executa a baixa atômica de estoque de todas as peças (H15).
    Se faltar 1 unidade em qualquer peça, faz rollback completo e mantém a OS Pendente.
    """
    if not is_dono_ou_gerente(request.user):
        raise PermissionDenied('Apenas Dono/Gerente pode aprovar Ordens de Serviço.')

    with transaction.atomic():
        ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)

        if ordem.status != 'pendente':
            messages.error(request, f'A OS #{ordem.pk} não está pendente (status atual: {ordem.get_status_display()}).')
            return redirect('core:aprovar_os_painel')

        if ordem.estoque_baixado:
            messages.error(request, f'A OS #{ordem.pk} já teve baixa de estoque registrada anteriormente.')
            return redirect('core:aprovar_os_painel')

        itens = list(
            ItemPeca.objects.select_related('peca')
            .filter(ordem=ordem)
            .order_by('peca_id')
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
                    f'{peca.descricao} (solicitado: {item.quantidade} un, disponível: {peca.estoque} un)'
                )

        if insuficientes:
            messages.error(
                request,
                f'Aprovação bloqueada para a OS #{ordem.pk} por estoque insuficiente: ' + '; '.join(insuficientes)
            )
            return redirect('core:aprovar_os_detalhe', pk=ordem.pk)

        for item in itens:
            peca = pecas_bloqueadas[item.peca_id]
            peca.estoque -= item.quantidade
            peca.save(update_fields=['estoque', 'atualizado_em'])

        ordem.status = 'aprovada'
        ordem.estoque_baixado = True
        ordem.aprovada_em = timezone.now()
        ordem.save(update_fields=['status', 'estoque_baixado', 'aprovada_em', 'atualizado_em'])

    messages.success(
        request,
        f'OS #{ordem.pk} aprovada com sucesso! Baixa atômica de estoque realizada e enviada para a fila da oficina.'
    )
    return redirect('core:aprovar_os_painel')


@login_required
def historico_placa(request):
    """
    Consulta rápida (< 3s) de histórico completo de manutenção por placa do veículo (H05).
    Distingue claramente:
      (a) Placa não cadastrada no sistema (CT-012)
      (b) Veículo cadastrado, porém sem histórico de manutenção/OSs (CT-059)
      (c) Veículo com histórico de OSs e valores congelados (CT-011)
    """
    if not is_atendente_ou_superior(request.user):
        raise PermissionDenied('Acesso restrito aos perfis Atendente e Dono/Gerente.')

    placa_raw = request.GET.get('placa', '').strip()
    placa_normalizada = re.sub(r'[\s-]+', '', placa_raw).upper()
    busca_realizada = bool(placa_normalizada)

    veiculo = None
    ordens_historico = []
    placa_nao_encontrada = False
    sem_historico_manutencao = False
    total_investido = Decimal('0.00')

    if busca_realizada:
        veiculo = (
            Veiculo.objects.select_related('cliente')
            .filter(placa__iexact=placa_normalizada)
            .first()
        )
        if not veiculo:
            placa_nao_encontrada = True
        else:
            ordens_historico = list(
                OrdemServico.objects.filter(veiculo=veiculo)
                .select_related('cliente', 'veiculo')
                .prefetch_related('itens_peca__peca', 'itens_servico__servico')
                .order_by('-criado_em', '-id')
            )
            if not ordens_historico:
                sem_historico_manutencao = True
            else:
                total_investido = sum(
                    (o.total for o in ordens_historico if o.status != 'cancelada'),
                    Decimal('0.00')
                )

    placas_recentes = Veiculo.objects.select_related('cliente').order_by('-id')[:8]

    context = {
        'titulo': 'Histórico por Placa',
        'termo_placa': placa_normalizada or placa_raw,
        'busca_realizada': busca_realizada,
        'veiculo': veiculo,
        'ordens_historico': ordens_historico,
        'placa_nao_encontrada': placa_nao_encontrada,
        'sem_historico_manutencao': sem_historico_manutencao,
        'total_investido': total_investido,
        'placas_recentes': placas_recentes,
    }
    return render(request, 'veiculos/historico_placa.html', context)


@login_required
def mecanico_os_dia(request):
    """
    Painel Operacional do Mecânico com a fila de OSs aprovadas e em execução do dia (H16, H17, H18).
    """
    if not is_mecanico_ou_gerente(request.user):
        raise PermissionDenied('Acesso restrito ao perfil Mecânico ou Dono/Gerente.')

    hoje = timezone.localdate()
    ordens_fila = (
        OrdemServico.objects.filter(status__in=['aprovada', 'em_execucao'])
        .annotate(data_operacional=Coalesce('aprovada_em', 'atualizado_em'))
        .filter(data_operacional__date=hoje)
        .select_related('cliente', 'veiculo')
        .prefetch_related('itens_peca__peca', 'itens_servico__servico')
        .order_by('id')
    )

    ordens_concluidas_hoje = (
        OrdemServico.objects.filter(status='concluida', data_conclusao__date=hoje)
        .select_related('cliente', 'veiculo')
        .order_by('-data_conclusao')[:10]
    )

    context = {
        'titulo': 'Painel do Mecânico — Fila do Dia',
        'hoje': hoje,
        'ordens_fila': ordens_fila,
        'ordens_concluidas_hoje': ordens_concluidas_hoje,
        'total_aprovadas': ordens_fila.filter(status='aprovada').count(),
        'total_em_execucao': ordens_fila.filter(status='em_execucao').count(),
        'total_concluidas_hoje': ordens_concluidas_hoje.count(),
    }
    return render(request, 'mecanico/os_dia.html', context)


@login_required
@require_POST
def mecanico_confirmar_peca(request, pk, item_id):
    """
    Confirmação de peças aplicadas pelo Mecânico (H17).
    Registra a quantidade efetivamente utilizada até o limite aprovado na OS,
    mudando o status para 'em_execucao' SEM realizar nova baixa no estoque.
    """
    if not is_mecanico_ou_gerente(request.user):
        raise PermissionDenied('Apenas o Mecânico ou Dono/Gerente pode confirmar o uso de peças.')

    with transaction.atomic():
        ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)
        if ordem.status not in {'aprovada', 'em_execucao'}:
            messages.error(request, 'Apenas OSs aprovadas ou em execução permitem confirmar uso de peças.')
            return redirect('core:mecanico_os_dia')

        item = get_object_or_404(ItemPeca.objects.select_for_update(), pk=item_id, ordem=ordem)
        try:
            qtd_utilizada = int(request.POST.get('quantidade_utilizada', ''))
        except (ValueError, TypeError):
            messages.error(request, 'Informe uma quantidade inteira válida.')
            return redirect('core:mecanico_os_dia')

        if qtd_utilizada < 0 or qtd_utilizada > item.quantidade:
            messages.error(
                request,
                f'A quantidade utilizada ({qtd_utilizada}) deve estar entre 0 e a quantidade aprovada ({item.quantidade}).'
            )
            return redirect('core:mecanico_os_dia')

        # H17: Atualiza apenas quantidade_utilizada no ItemPeca; Peca.estoque NÃO é alterado!
        item.quantidade_utilizada = qtd_utilizada
        item.save(update_fields=['quantidade_utilizada'])

        if ordem.status == 'aprovada':
            ordem.status = 'em_execucao'
            ordem.save(update_fields=['status', 'atualizado_em'])

    messages.success(
        request,
        f'Uso confirmado na OS #{ordem.pk}: {item.quantidade_utilizada}/{item.quantidade} un. de "{item.peca.descricao}" (sem nova baixa de estoque).'
    )
    return redirect('core:mecanico_os_dia')


@login_required
@require_POST
def mecanico_concluir_os(request, pk):
    """
    Encerra a execução técnica da Ordem de Serviço registrando data e hora de conclusão (H18).
    """
    if not is_mecanico_ou_gerente(request.user):
        raise PermissionDenied('Apenas o Mecânico ou Dono/Gerente pode concluir uma Ordem de Serviço.')

    with transaction.atomic():
        ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)
        if ordem.status not in {'aprovada', 'em_execucao'}:
            messages.error(request, f'A OS #{ordem.pk} não pode ser concluída pois está com status "{ordem.get_status_display()}".')
            return redirect('core:mecanico_os_dia')

        ordem.status = 'concluida'
        ordem.data_conclusao = timezone.now()
        ordem.save(update_fields=['status', 'data_conclusao', 'atualizado_em'])

    messages.success(
        request,
        f'Ordem de Serviço #{ordem.pk} ({ordem.veiculo.placa}) concluída com sucesso em {ordem.data_conclusao.strftime("%d/%m/%Y às %H:%M")}!'
    )
    return redirect('core:mecanico_os_dia')


# ==============================================================================
# SPRINT 4 (E8): DASHBOARD ANALÍTICO E RELATÓRIOS GERENCIAIS (H19, H20, H21)
# ==============================================================================

@login_required
def relatorios_dashboard(request):
    """
    Dashboard Analítico exclusivo para Dono/Gerente (H19, H20, H21).
    - H19: Faturamento mensal líquido (soma apenas OSs com status='concluida' sem duplicação N:N)
    - H20: Ranking de Serviços mais executados (decrescente + desempate por descrição)
    - H21: Ranking de Peças mais vendidas (decrescente + desempate por descrição)
    """
    if not is_dono_ou_gerente(request.user):
        raise PermissionDenied('Relatórios gerenciais são exclusivos para o perfil Dono/Gerente.')

    inicio_str = request.GET.get('inicio', '').strip()
    fim_str = request.GET.get('fim', '').strip()

    qs_concluidas = OrdemServico.objects.filter(status='concluida').annotate(
        data_ref=Coalesce('data_conclusao', 'atualizado_em')
    )

    data_inicio = None
    data_fim = None
    try:
        if inicio_str:
            data_inicio = date.fromisoformat(inicio_str)
            qs_concluidas = qs_concluidas.filter(data_ref__date__gte=data_inicio)
        if fim_str:
            data_fim = date.fromisoformat(fim_str)
            qs_concluidas = qs_concluidas.filter(data_ref__date__lte=data_fim)
    except ValueError:
        messages.warning(request, 'Período informado em formato inválido. Exibindo todos os períodos.')
        inicio_str = ''
        fim_str = ''

    # 1. Faturamento Mensal (H19) — Agregado diretamente em OrdemServico (sem JOIN N:N)
    faturamento_por_mes_qs = (
        qs_concluidas
        .annotate(mes=TruncMonth('data_ref'))
        .values('mes')
        .annotate(
            quantidade_os=Count('id', distinct=True),
            subtotal_bruto=Coalesce(
                Sum('subtotal'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            descontos=Coalesce(
                Sum('valor_desconto'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            faturamento_liquido=Coalesce(
                Sum('total'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
        )
        .order_by('mes')
    )

    faturamento_mensal_lista = []
    for item in faturamento_por_mes_qs:
        mes_dt = item['mes']
        mes_label = mes_dt.strftime('%m/%Y') if mes_dt else 'Sem Data'
        faturamento_mensal_lista.append({
            'mes_iso': mes_dt.strftime('%Y-%m') if mes_dt else '',
            'mes_label': mes_label,
            'quantidade_os': item['quantidade_os'],
            'subtotal_bruto': item['subtotal_bruto'],
            'descontos': item['descontos'],
            'faturamento_liquido': item['faturamento_liquido'],
        })

    # Indicadores consolidados do período filtrado
    total_os_concluidas = sum(m['quantidade_os'] for m in faturamento_mensal_lista)
    faturamento_total_liquido = sum((m['faturamento_liquido'] for m in faturamento_mensal_lista), Decimal('0.00'))
    total_descontos = sum((m['descontos'] for m in faturamento_mensal_lista), Decimal('0.00'))
    ticket_medio = (
        (faturamento_total_liquido / Decimal(total_os_concluidas)).quantize(Decimal('0.01'))
        if total_os_concluidas > 0 else Decimal('0.00')
    )

    concluidas_ids = qs_concluidas.values_list('id', flat=True)

    # 2. Ranking de Serviços Mais Executados (H20) — Desempate alfabético por descrição
    ranking_servicos = list(
        ItemServico.objects.filter(ordem_id__in=concluidas_ids)
        .values('servico_id', 'servico__descricao')
        .annotate(
            quantidade_executada=Sum('quantidade'),
            total_ordens=Count('ordem_id', distinct=True),
            receita_historica=Coalesce(
                Sum(
                    F('quantidade') * F('preco_unitario_historico'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                ),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        .order_by('-quantidade_executada', 'servico__descricao')
    )

    # 3. Ranking de Peças Mais Vendidas (H21) — Desempate alfabético por descrição
    ranking_pecas = list(
        ItemPeca.objects.filter(ordem_id__in=concluidas_ids)
        .values('peca_id', 'peca__descricao')
        .annotate(
            quantidade_vendida=Sum('quantidade'),
            total_ordens=Count('ordem_id', distinct=True),
            receita_historica=Coalesce(
                Sum(
                    F('quantidade') * F('preco_unitario_historico'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                ),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        .order_by('-quantidade_vendida', 'peca__descricao')
    )

    # Dados serializados para o Chart.js
    chart_faturamento_data = {
        'labels': [m['mes_label'] for m in faturamento_mensal_lista],
        'faturamento': [float(m['faturamento_liquido']) for m in faturamento_mensal_lista],
        'descontos': [float(m['descontos']) for m in faturamento_mensal_lista],
        'quantidade_os': [m['quantidade_os'] for m in faturamento_mensal_lista],
    }
    chart_servicos_data = {
        'labels': [s['servico__descricao'] for s in ranking_servicos[:8]],
        'quantidades': [s['quantidade_executada'] for s in ranking_servicos[:8]],
        'receitas': [float(s['receita_historica']) for s in ranking_servicos[:8]],
    }
    chart_pecas_data = {
        'labels': [p['peca__descricao'] for p in ranking_pecas[:8]],
        'quantidades': [p['quantidade_vendida'] for p in ranking_pecas[:8]],
        'receitas': [float(p['receita_historica']) for p in ranking_pecas[:8]],
    }

    context = {
        'titulo': 'Relatórios Gerenciais & Faturamento',
        'inicio': inicio_str,
        'fim': fim_str,
        'faturamento_mensal': faturamento_mensal_lista,
        'ranking_servicos': ranking_servicos,
        'ranking_pecas': ranking_pecas,
        'total_os_concluidas': total_os_concluidas,
        'faturamento_total_liquido': faturamento_total_liquido,
        'total_descontos': total_descontos,
        'ticket_medio': ticket_medio,
        'chart_faturamento_json': json.dumps(chart_faturamento_data),
        'chart_servicos_json': json.dumps(chart_servicos_data),
        'chart_pecas_json': json.dumps(chart_pecas_data),
    }
    return render(request, 'relatorios/dashboard.html', context)


# ==============================================================================
# ENDPOINTS TRANSACIONAIS E API DE BACKEND CONSOLIDADOS (FELIPE — SPRINTS 1 A 4)
# ==============================================================================

def _decimal(valor, nome):
    try:
        resultado = Decimal(str(valor or '0'))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError(f'{nome} inválido.')
    return resultado


@exigir_perfil(PERFIL_DONO)
@require_http_methods(['GET', 'POST'])
def catalogo_pecas(request):
    """Lista e cadastra peças (Exclusivo Dono/Gerente — H06)."""
    form = PecaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            peca = form.save()
        messages.success(request, f'Peça "{peca.descricao}" cadastrada.')
        return redirect('core:sprint1_pecas')

    busca = request.GET.get('busca', '').strip()
    pecas = Peca.objects.all()
    if busca:
        pecas = pecas.filter(descricao__icontains=busca)
    return render(request, 'catalogo/pecas_list_form.html', {
        'titulo': 'Catálogo de Peças',
        'pecas': pecas,
        'form': form,
        'termo_busca': busca,
    })


@exigir_perfil(PERFIL_DONO)
@require_http_methods(['GET', 'POST'])
def catalogo_servicos(request):
    """Lista e cadastra serviços (Exclusivo Dono/Gerente — H07)."""
    form = ServicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            servico = form.save()
        messages.success(request, f'Serviço "{servico.descricao}" cadastrado.')
        return redirect('core:sprint1_servicos')

    busca = request.GET.get('busca', '').strip()
    servicos = Servico.objects.all()
    if busca:
        servicos = servicos.filter(descricao__icontains=busca)
    return render(request, 'catalogo/servicos_list_form.html', {
        'titulo': 'Catálogo de Serviços',
        'servicos': servicos,
        'form': form,
        'termo_busca': busca,
    })


@exigir_perfil(PERFIL_DONO)
@require_POST
def excluir_peca_sem_vinculo(request, pk):
    """Exclui peça apenas quando não há ItemPeca apontando para ela (H09)."""
    peca = get_object_or_404(Peca, pk=pk)
    if peca.itens_os.exists():
        messages.error(request, 'Peças vinculadas a OS não podem ser excluídas.')
    else:
        peca.delete()
        messages.success(request, 'Peça excluída do catálogo.')
    return redirect('core:sprint1_pecas')


@exigir_perfil(PERFIL_DONO)
@require_POST
def excluir_servico_sem_vinculo(request, pk):
    """Exclui serviço apenas quando não há ItemServico apontando para ele (H09)."""
    servico = get_object_or_404(Servico, pk=pk)
    if servico.itens_os.exists():
        messages.error(request, 'Serviços vinculados a OS não podem ser excluídos.')
    else:
        servico.delete()
        messages.success(request, 'Serviço excluído do catálogo.')
    return redirect('core:sprint1_servicos')


@exigir_perfil(*PERFIS_ORCAMENTO)
@require_POST
def converter_orcamento_em_os(request):
    """Cria uma OS pendente congelando os preços do catálogo sem baixar estoque (H12)."""
    cliente = get_object_or_404(Cliente, pk=request.POST.get('cliente'))
    veiculo = get_object_or_404(Veiculo, pk=request.POST.get('veiculo'), cliente=cliente)
    desconto = _decimal(request.POST.get('desconto_percentual', 0), 'Desconto')
    if not Decimal('0') <= desconto <= Decimal('100'):
        raise ValidationError('O desconto deve estar entre 0 e 100%.')

    pecas = request.POST.getlist('pecas_id[]')
    qtd_pecas = request.POST.getlist('pecas_qtd[]')
    servicos = request.POST.getlist('servicos_id[]')
    qtd_servicos = request.POST.getlist('servicos_qtd[]')
    if not pecas and not servicos:
        raise ValidationError('A OS deve conter ao menos um item.')

    try:
        with transaction.atomic():
            ordem = OrdemServico.objects.create(
                cliente=cliente, veiculo=veiculo, status='pendente',
                desconto_percentual=desconto,
                observacoes=request.POST.get('observacoes', '').strip(),
            )
            for pk, raw_qtd in zip(pecas, qtd_pecas):
                if not pk:
                    continue
                peca = Peca.objects.get(pk=pk)
                qtd = int(raw_qtd)
                if qtd <= 0:
                    raise ValidationError('A quantidade da peça deve ser positiva.')
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
                    raise ValidationError('A quantidade do serviço deve ser positiva.')
                ItemServico.objects.create(
                    ordem=ordem, servico=servico, quantidade=qtd,
                    preco_unitario_historico=servico.preco,
                )
            recalcular_ordem(ordem)
    except (Peca.DoesNotExist, Servico.DoesNotExist, ValueError, IntegrityError) as exc:
        raise ValidationError(f'Itens inválidos ou duplicados: {exc}')

    return JsonResponse({
        'id': ordem.pk,
        'status': ordem.status,
        'total': str(ordem.total),
        'estoque_baixado': False,
    }, status=201)


@exigir_perfil(PERFIL_DONO)
@require_POST
def ajustar_estoque_api(request, pk):
    """Ajusta estoque com lock de linha e bloqueio de saldo negativo (H08)."""
    operacao = request.POST.get('operacao')
    try:
        quantidade = int(request.POST.get('quantidade', ''))
    except ValueError:
        raise ValidationError('Quantidade deve ser um número inteiro.')
    if quantidade < 0 or operacao not in {'adicionar', 'remover', 'definir'}:
        raise ValidationError('Operação ou quantidade inválida.')

    with transaction.atomic():
        peca = Peca.objects.select_for_update().get(pk=pk)
        if operacao == 'adicionar':
            novo_saldo = peca.estoque + quantidade
        elif operacao == 'remover':
            novo_saldo = peca.estoque - quantidade
        else:
            novo_saldo = quantidade
        if novo_saldo < 0:
            raise ValidationError('Ajuste recusado: o estoque não pode ficar negativo.')
        anterior = peca.estoque
        peca.estoque = novo_saldo
        peca.save(update_fields=['estoque', 'atualizado_em'])

    return JsonResponse({'peca': peca.pk, 'anterior': anterior, 'estoque': novo_saldo})


@exigir_perfil(PERFIL_DONO)
@require_POST
def excluir_peca_protegida_api(request, pk):
    """Exclui somente peça sem vínculo histórico com item de OS (H09)."""
    with transaction.atomic():
        peca = Peca.objects.select_for_update().get(pk=pk)
        if peca.itens_os.exists():
            raise ValidationError('Peça vinculada a OS não pode ser excluída.')
        peca.delete()
    return JsonResponse({'excluida': True})


@exigir_perfil(PERFIL_DONO)
@require_POST
@transaction.atomic
def aprovar_os(request, pk):
    """Aprova e baixa toda a OS em uma única transação serializável por linhas (H15)."""
    ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)
    if ordem.status != 'pendente':
        raise ValidationError('Somente OS pendente pode ser aprovada.')
    if ordem.estoque_baixado:
        raise ValidationError('Esta OS já teve baixa de estoque.')

    itens = list(
        ItemPeca.objects.select_related('peca')
        .filter(ordem=ordem)
        .order_by('peca_id')
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
                f'{peca.descricao}: disponível {peca.estoque}, necessário {item.quantidade}'
            )
    if insuficientes:
        raise ValidationError('Estoque insuficiente: ' + '; '.join(insuficientes))

    for item in itens:
        peca = pecas_bloqueadas[item.peca_id]
        peca.estoque -= item.quantidade
        peca.save(update_fields=['estoque', 'atualizado_em'])

    ordem.status = 'aprovada'
    ordem.estoque_baixado = True
    ordem.aprovada_em = timezone.now()
    ordem.save(update_fields=['status', 'estoque_baixado', 'aprovada_em', 'atualizado_em'])

    return JsonResponse({'os': ordem.pk, 'status': ordem.status, 'baixa': True})


@exigir_perfil(PERFIL_MECANICO)
@require_POST
@transaction.atomic
def confirmar_uso_peca(request, pk, item_id):
    """Registra consumo real pelo mecânico sem mexer novamente no estoque (H17)."""
    ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)
    if ordem.status not in {'aprovada', 'em_execucao'}:
        raise ValidationError('A OS precisa estar aprovada ou em execução.')

    item = get_object_or_404(ItemPeca.objects.select_for_update(), pk=item_id, ordem=ordem)
    try:
        quantidade_utilizada = int(request.POST.get('quantidade_utilizada', ''))
    except ValueError:
        raise ValidationError('Quantidade utilizada inválida.')
    if quantidade_utilizada < 0 or quantidade_utilizada > item.quantidade:
        raise ValidationError('Uso deve estar entre zero e a quantidade aprovada.')

    item.quantidade_utilizada = quantidade_utilizada
    item.save(update_fields=['quantidade_utilizada'])
    if ordem.status == 'aprovada':
        ordem.status = 'em_execucao'
        ordem.save(update_fields=['status', 'atualizado_em'])

    return JsonResponse({
        'os': ordem.pk,
        'item': item.pk,
        'quantidade_utilizada': item.quantidade_utilizada,
        'estoque_baixado_novamente': False,
    })


@exigir_perfil(PERFIL_MECANICO)
@require_POST
@transaction.atomic
def concluir_os(request, pk):
    """Conclui uma OS em execução e grava o instante de encerramento (H18)."""
    ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=pk)
    if ordem.status != 'em_execucao':
        raise ValidationError('Somente OS em execução pode ser concluída.')
    ordem.status = 'concluida'
    ordem.data_conclusao = timezone.now()
    ordem.save(update_fields=['status', 'data_conclusao', 'atualizado_em'])
    return JsonResponse({'os': ordem.pk, 'status': ordem.status})


@exigir_perfil(PERFIL_DONO)
@require_GET
def faturamento_mensal(request):
    """Retorna faturamento líquido somente de OS concluídas sem duplicação N:N (H19)."""
    qs = OrdemServico.objects.filter(status='concluida')
    inicio = request.GET.get('inicio')
    fim = request.GET.get('fim')
    if inicio:
        qs = qs.filter(data_conclusao__date__gte=date.fromisoformat(inicio))
    if fim:
        qs = qs.filter(data_conclusao__date__lte=date.fromisoformat(fim))

    linhas = (
        qs.exclude(data_conclusao__isnull=True)
        .annotate(mes=TruncMonth('data_conclusao'))
        .values('mes')
        .annotate(
            quantidade_os=Count('id', distinct=True),
            faturamento=Coalesce(
                Sum('total'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            descontos=Coalesce(
                Sum('valor_desconto'),
                Decimal('0.00'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        .order_by('mes')
    )
    resultado = [
        {
            'mes': linha['mes'].strftime('%Y-%m'),
            'quantidade_os': linha['quantidade_os'],
            'faturamento': f"{Decimal(linha['faturamento']):.2f}",
            'descontos': f"{Decimal(linha['descontos']):.2f}",
        }
        for linha in linhas
    ]
    return JsonResponse({'resultados': resultado})
