from django import template

register = template.Library()

@register.filter
def dotfloat(value, decimals=2):
    try:
        decimals = int(decimals)
        return format(float(value or 0), f'.{decimals}f')
    except (TypeError, ValueError):
        return format(0.0, f'.{int(decimals) if decimals else 0}f')
