from constance import config
from django import forms
from django.contrib.auth import login, password_validation
from django.contrib.auth.backends import ModelBackend
from django.db import transaction
from django.http import HttpResponseNotFound
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin, ProcessFormView
from strategy_field.utils import fqn

from bitcaster.framework.db.fields import ROLES
from bitcaster.models import Application, Event, Organization, User
from bitcaster.models.audit import AuditEvent
from bitcaster.models.organization import RESERVED_ORGANIZATION_NAME
from bitcaster.models.validators import ListValidator, NameValidator

__all__ = ['SetupView']


class SetupForm(forms.Form):
    error_messages = {'password_mismatch': _('Passwords do not match')}

    organization = forms.CharField(validators=[ListValidator(RESERVED_ORGANIZATION_NAME),
                                               NameValidator(),
                                               ])
    email = forms.EmailField()
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class SetupView(TemplateView, FormMixin, ProcessFormView):
    template_name = 'bitcaster/setup.html'
    form_class = SetupForm

    def get_success_url(self):
        return reverse('settings')

    def get(self, request, *args, **kwargs):
        if bool(config.INITIALIZED):
            return HttpResponseNotFound('Not Found')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            name = form.cleaned_data['organization']
            user = User.objects.create_superuser(form.cleaned_data['email'],
                                                 form.cleaned_data['password1'])

            configure_system(name, user)
            config.SYSTEM_CONFIGURED = 0
            config.INITIALIZED = 1
            login(self.request, user, fqn(ModelBackend))
        return super().form_valid(form)


def configure_system(name, owner):
    org = Organization.objects.create(name=name,
                                      slug=slugify(name),
                                      admin_email=owner.email,
                                      is_core=True,
                                      owner=owner)
    org.add_member(owner, role=ROLES.OWNER, date_enrolled=timezone.now())
    bitcaster = Application.objects.create(name='Bitcaster',
                                           organization=org,
                                           core=True)
    for evt in AuditEvent:
        Event.objects.create(application=bitcaster,
                             core=True,
                             name=evt.name,
                             subscription_policy=Event.POLICIES.MEMBERS)
