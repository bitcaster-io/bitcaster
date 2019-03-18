from django.forms.widgets import Input


class PasswordEyeInput(Input):
    input_type = 'password'
    template_name = 'django/forms/widgets/password-eye.html'
