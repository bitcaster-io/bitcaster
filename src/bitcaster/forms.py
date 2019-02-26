from django.forms.widgets import Input
from strategy_field.forms import StrategyFormField
from strategy_field.utils import fqn


class PasswordEyeInput(Input):
    input_type = 'password'
    template_name = 'django/forms/widgets/password-eye.html'


class DispatcherFormField(StrategyFormField):
    def has_changed(self, initial, data):
        ret = super().has_changed(initial, data)
        if ret and initial and data:
            return fqn(initial) != data
        return ret
