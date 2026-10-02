from itertools import chain

from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404

from .calculos import calcular_totais
from .models import OrdemServico, ItemPeca, ItemServico, Peca, Servico


TIPOS_ITEM = {'peca': (ItemPeca, Peca), 'servico': (ItemServico, Servico)}


def ordem_pendente_bloqueada(ordem_id):
    # Chamado dentro de atomic. Serializa alterações na mesma OS no PostgreSQL.
    ordem = get_object_or_404(OrdemServico.objects.select_for_update(), pk=ordem_id)
    if ordem.status != 'pendente':
        raise ValidationError('Somente ordens pendentes podem ter itens ou desconto alterados.')
    return ordem


def recalcular_ordem(ordem):
    itens = chain(
        ordem.itens_peca.values_list('quantidade', 'preco_unitario_historico'),
        ordem.itens_servico.values_list('quantidade', 'preco_unitario_historico'),
    )
    ordem.subtotal, ordem.valor_desconto, ordem.total = calcular_totais(itens, ordem.desconto_percentual)
    ordem.full_clean()
    ordem.save(update_fields=['desconto_percentual', 'subtotal', 'valor_desconto', 'total'])


@transaction.atomic
def incluir_item(ordem_id, tipo, catalogo_id, quantidade):
    ordem = ordem_pendente_bloqueada(ordem_id)
    modelo_item, modelo_catalogo = TIPOS_ITEM[tipo]
    catalogo = get_object_or_404(modelo_catalogo, pk=catalogo_id)
    item = modelo_item(ordem=ordem, quantidade=quantidade, preco_unitario_historico=catalogo.preco, **{tipo: catalogo})
    # O preço é copiado do catálogo pelo servidor, preservando o histórico.
    item.full_clean()
    item.save()
    recalcular_ordem(ordem)
    return item


@transaction.atomic
def remover_item(ordem_id, tipo, item_id):
    ordem = ordem_pendente_bloqueada(ordem_id)
    modelo_item, _ = TIPOS_ITEM[tipo]
    item = get_object_or_404(modelo_item, pk=item_id, ordem=ordem)
    item.delete()
    recalcular_ordem(ordem)


@transaction.atomic
def alterar_desconto(ordem_id, desconto):
    ordem = ordem_pendente_bloqueada(ordem_id)
    ordem.desconto_percentual = desconto
    recalcular_ordem(ordem)
    return ordem
