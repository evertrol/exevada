from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def lower_bnd(value):
    return mark_safe("-&#8734;") if value == "None" else value

@register.filter
@stringfilter
def upper_bnd(value):
    return mark_safe("+&#8734;") if value == "None" else value