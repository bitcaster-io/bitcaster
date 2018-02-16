# -*- coding: utf-8 -*-
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_countries.fields import CountryField
from timezone_field import TimeZoneField

from mercury import logging
from mercury.fields import EncryptedJSONField
from mercury.models.fields import LanguageField

logger = logging.getLogger(__name__)


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
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

    timezone = TimeZoneField()
    language = LanguageField(default='en')
    country = CountryField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def get_short_name(self):
        return self.first_name

    def is_admin(self, application):
        return application.owner == self or application.maintainers.filter(id=self.pk).exists()

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
