from django import template
from datetime import date, timedelta

register = template.Library()

@register.filter
def get_values(value):
    return value[0].value
