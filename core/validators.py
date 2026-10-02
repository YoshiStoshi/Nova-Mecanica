import re

from django.core.exceptions import ValidationError


def normalizar_cpf(valor):
    valor = valor.strip()
    if not re.fullmatch(r'(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})', valor):
        raise ValidationError('Informe um CPF válido com 11 dígitos, com ou sem pontuação.')
    cpf = re.sub(r'[^0-9]', '', valor)
    if len(set(cpf)) == 1:
        raise ValidationError('Informe um CPF válido.')
    for tamanho in (9, 10):
        soma = sum(int(cpf[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10 % 11) % 10
        if int(cpf[tamanho]) != digito:
            raise ValidationError('Informe um CPF válido.')
    return cpf


def normalizar_placa(valor):
    placa = valor.strip().upper().replace('-', '').replace(' ', '')
    if not re.fullmatch(r'[A-Z]{3}(?:[0-9]{4}|[0-9][A-Z][0-9]{2})', placa):
        raise ValidationError('Use uma placa no formato ABC-1234 ou ABC1D23.')
    return placa
