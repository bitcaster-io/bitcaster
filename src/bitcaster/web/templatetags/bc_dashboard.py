from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def metric(label, value):
    return mark_safe(f'''<div class="block p-1">
                <div class="d-inline-block">{label}</div>
                <div class="d-inline-block pull-right">{value}</div>
            </div>''')
