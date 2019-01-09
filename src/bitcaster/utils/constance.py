from constance import config
from django.contrib.auth.models import Group
from django.forms import ChoiceField, HiddenInput, Select, Textarea, TextInput
from django.template import Context, Template
from django.utils.safestring import mark_safe


class GroupChoiceField(ChoiceField):

    def __init__(self, **kwargs):
        names = list(Group.objects.values_list('name', flat=True))
        choices = zip(names, names)
        super().__init__(choices=choices, **kwargs)


class GroupChoice(Select):
    pass


# class LabelInput(HiddenInput):
#
#     def render(self, name, value, attrs=None, renderer=None):
#         context = self.get_context(name, value, attrs)
#         context['value'] = str(value)
#         tpl = Template('<input type="hidden" name="{{ widget.name }}" value="{{ value }}">{{ value }}')
#         return mark_safe(tpl.render(Context(context)))
#

class ObfuscatedInput(HiddenInput):

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        context['value'] = str(value)
        context['label'] = 'Set' if value else 'Not Set'

        tpl = Template('<input type="hidden" name="{{ widget.name }}" value="{{ value }}">{{ label }}')
        return mark_safe(tpl.render(Context(context)))


class WriteOnlyWidget:
    def format_value(self, value):
        value = '***'
        return super().format_value(value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value == '***':
            return getattr(config, name)
        return value


class WriteOnlyTextarea(WriteOnlyWidget, Textarea):
    pass


class WriteOnlyInput(WriteOnlyWidget, TextInput):
    pass
