import ast

from constance import config
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import (CharField, ChoiceField, HiddenInput,
                          Select, Textarea, TextInput,)
from django.template import Context, Template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class GroupChoiceField(ChoiceField):

    def __init__(self, **kwargs):
        names = list(Group.objects.values_list('name', flat=True))
        choices = zip(names, names)
        super().__init__(choices=choices, **kwargs)


class GroupChoice(Select):
    pass


class LdapDNField(CharField):
    def clean(self, value):
        if value in self.empty_values and self.required:
            raise ValidationError(self.error_messages['required'], code='required')
        elif value not in self.empty_values:
            try:
                entries = value.split(',')
                for entry in entries:
                    k, v = entry.split('=')
                    if not (k and v):
                        raise ValidationError(_('%s cannot be empty') % k)
            except ValueError:
                raise ValidationError(_('Invalid value %s. Use key=value,key1=value1... synthax') % value)
            if r'%(user)s' not in value:
                raise ValidationError(_("DN Template must contains '%(user)s' mapping"))
        return value


class FieldMappingField(CharField):

    def clean(self, value):
        if value in self.empty_values and self.required:
            raise ValidationError(self.error_messages['required'], code='required')
        return self.to_python(value)

    def prepare_value(self, value):
        if not isinstance(value, dict):
            try:
                value = ast.literal_eval(value)
            except (SyntaxError, ValueError):
                value = self.to_python(value)
        if not isinstance(value, dict):
            raise ValidationError(_('Invalid value %s. Ie. email:mail,.. synthax') % value)
        return ','.join(['%s:%s' % (k, v) for k, v in value.items()])

    def to_python(self, value):
        if not value:
            return value
        ret = {}
        try:
            entries = value.split(',')
            for entry in entries:
                k, v = entry.split(':')
                if not (k and v):
                    raise ValidationError(_('%s cannot be empty') % k)
                ret[k] = v
        except (ValueError, AttributeError, TypeError):
            raise ValidationError(_('Invalid value %s. Ie. email:mail,.. synthax') % value)
        return ret


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
