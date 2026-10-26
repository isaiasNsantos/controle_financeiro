from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def moeda(valor):
    if valor is None:
        return "0,00"
    try:
        # Formata com 2 casas decimais e troca o ponto por vírgula
        return f"{float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return valor

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)