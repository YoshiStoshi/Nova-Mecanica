from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.core.exceptions import ValidationError


CENTAVO = Decimal('0.01')


def calcular_totais(itens, desconto=Decimal('0')):
    """H11: itens são pares (quantidade, preço unitário), sem usar float.

    A mesma função pode ser usada pelo futuro formulário de orçamento.
    Arredondamos o total final e derivamos o desconto para fechar os centavos.
    """
    try:
        if isinstance(desconto, float):
            raise ValueError
        desconto = Decimal(desconto)
        if not desconto.is_finite() or not 0 <= desconto <= 100:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        raise ValidationError('O desconto deve estar entre 0% e 100%.')

    subtotal = Decimal('0.00')
    for quantidade, preco in itens:
        try:
            if isinstance(preco, float) or isinstance(quantidade, bool):
                raise ValueError
            preco = Decimal(preco)
            if not isinstance(quantidade, int) or quantidade <= 0:
                raise ValueError
            if not preco.is_finite() or preco < 0 or preco != preco.quantize(CENTAVO):
                raise ValueError
            subtotal += quantidade * preco
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError('Informe quantidade inteira positiva e preço não negativo com até duas casas decimais.')
    subtotal = subtotal.quantize(CENTAVO)
    total = (subtotal * (1 - desconto / 100)).quantize(CENTAVO, rounding=ROUND_HALF_UP)
    return subtotal, subtotal - total, total
