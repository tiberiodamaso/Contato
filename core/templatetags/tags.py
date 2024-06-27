import re
from django import template
from datetime import date, timedelta
from cards.utils import cleaner

register = template.Library()

@register.filter
def get_values(value):
    return value[0].value


@register.filter
def translate(value):
    if value == 'canceled':
        return 'Cancelada'
    if value == 'authorized':
        return 'Ativa'
    if value == 'paid':
        return 'Pago'
    return value


@register.filter
def formata_telefone(value):
    value = cleaner(value)
    return value


@register.filter
def formata_cod_pais(value):
    return value.codigo


@register.filter
def get_name(value):
    if value._meta.object_name == 'CartaoPF':
        return 'Cartão Pessoal'
    if value._meta.object_name == 'Ad':
        return 'Anúncios'
    if value._meta.object_name == 'Relatorio':
        return 'Relatório'
    return 'Cartão Empresarial'


@register.filter
def calculate(value):
    return 10 - value
