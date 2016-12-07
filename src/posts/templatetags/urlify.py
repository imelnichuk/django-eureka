try:
    from urllib import quote_plus
except:
    pass

try:
    from urllib.parse import quote_plus
except:
    pass

from django import template

register = template.library()

@register.filter
def urlify(value):
    return quote_plus(value)
