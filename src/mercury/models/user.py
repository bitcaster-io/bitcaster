# -*- coding: utf-8 -*-
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.core.mail import send_mail
from django.db import models
from django.template import Template, Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from oath import totp
from timezone_field import TimeZoneField

from mercury import logging
from mercury.fields import EncryptedJSONField, LanguageField
from mercury.utils.http import absolute_uri

logger = logging.getLogger(__name__)


class User(AbstractBaseUser, PermissionsMixin):
    title = models.CharField(max_length=5, blank=True, null=True)
    name = models.CharField(_('full name'), max_length=250, blank=True)
    friendly_name = models.CharField(_('display name'), max_length=250, blank=True,
                                     help_text="display/friendly name. Can be given name or nickname")
    email = models.EmailField(_('email address'), null=True,
                              unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_managed = models.BooleanField(
        _('managed'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as '
            'managed. Select this to disallow the user from '
            'modifying their account (username, password, etc).'
        )
    )
    is_password_expired = models.BooleanField(
        _('password expired'),
        default=False,
        help_text=_(
            'If set to true then the user needs to change the '
            'password on next sign in.'
        )
    )
    last_password_change = models.DateTimeField(
        _('date of last password change'),
        null=True,
        help_text=_('The date the password was changed last.')
    )
    date_joined = models.DateTimeField(
        _('date joined'), default=timezone.now)

    storage = EncryptedJSONField(
        _('storage'),
        blank=True, null=True,
        help_text=_('Where store handler related user data')

    )
    picture = models.ImageField(blank=True, null=True,
                                height_field='picture_height',
                                width_field='picture_width')
    picture_height = models.ImageField(editable=False)
    picture_width = models.ImageField(editable=False)
    timezone = TimeZoneField()
    language = LanguageField(default='en')
    country = CountryField()

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def set_password(self, raw_password):
        super(User, self).set_password(raw_password)
        self.last_password_change = timezone.now()
        self.is_password_expired = False

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        app_label = 'mercury'
        permissions = (('activate_user', 'Can activate user'),
                       )

    def send_confirmation_email(self):
        from oath.google_authenticator import from_b32key
        # check = totp(settings.OTP_KEY, period=settings.CONFIRM_EMAIL_EXPIRE)
        gauth = from_b32key(settings.OTP_KEY)
        check = gauth.generate()
        ctx = {
            'user': self,
            'url': absolute_uri(reverse('confirm-email',
                                        args=[self.id, check])
                                ),
            'confirm_email': self.email,
        }
        subject = '[Bitcaster] Confirm Email'

        message = get_template('bitcaster/emails/confirm_email.txt').render(ctx)
        html_message = get_template('bitcaster/emails/confirm_email.html').render(ctx)

        ret = send_mail(subject=subject,
                        message=message,
                        html_message=html_message,
                        from_email='bitcaster@os4d.org',
                        recipient_list=[self.email])
        return ret
