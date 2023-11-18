from django import template
from datetime import date, timedelta
from cards.utils import cleaner

register = template.Library()

@register.filter
def get_values(value):
    return value[0].value


@register.filter
def translate(value):
    if value == 'cancelled':
        return 'cancelada'
    if value == 'authorized':
        return 'ativa'
    return value


@register.filter
def formata_telefone(value):
    value = cleaner(value)
    return value

