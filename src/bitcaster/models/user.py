import logging

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (PermissionsMixin,
                                        UserManager as _UserManager,)
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
# from social_auth.backends.facebook import FacebookBackend
# from social_auth.backends import google
# from social_auth.signals import socialauth_registered
from django_redis import get_redis_connection
from timezone_field import TimeZoneField

from bitcaster.file_storage import MediaFileSystemStorage, profile_media_root
from bitcaster.framework.db.fields import EncryptedJSONField, LanguageField
from bitcaster.mail import send_mail_async
from bitcaster.security import APP_ROLES
from bitcaster.utils.cache import redis_property
from bitcaster.utils.http import absolute_uri

logger = logging.getLogger(__name__)
cache = get_redis_connection('default')


class UserManager(_UserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.pop('username', None)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'email'

    title = models.CharField(max_length=5, blank=True, null=True)
    name = models.CharField(_('full name'), max_length=250, blank=True)
    friendly_name = models.CharField(_('display name'), max_length=250, blank=True,
                                     help_text='display/friendly name. Can be given name or nickname')
    email = models.EmailField(_('email address'), null=True, unique=True)

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

    storage = EncryptedJSONField(_('storage'),
                                 default=dict,
                                 blank=True, null=True)

    options = EncryptedJSONField(_('options'),
                                 default=dict,
                                 blank=True, null=True)

    extras = JSONField(_('extras'),
                       default=dict,
                       blank=True, null=True)

    avatar = models.ImageField(blank=True, null=True,
                               # upload_to="pictures",
                               upload_to=profile_media_root,
                               storage=MediaFileSystemStorage(),
                               height_field='picture_height',
                               width_field='picture_width'
                               )
    picture_height = models.IntegerField(editable=False, null=True)
    picture_width = models.IntegerField(editable=False, null=True)
    timezone = TimeZoneField(verbose_name=_('Timezone'), null=True)
    language = LanguageField(verbose_name=_('Language'), default='en', null=True)
    country = CountryField(verbose_name=_('Country'), null=True)

    objects = UserManager()

    class Meta:
        app_label = 'bitcaster'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = (('activate_user', 'Can activate user'),
                       )

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        return self.friendly_name or self.email

    @redis_property
    def is_manager(self):
        # return true is user is a manager of any application
        return bool(self.memberships.filter(applications__role=APP_ROLES.ADMIN).exists())

    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.last_password_change = timezone.now()
        self.is_password_expired = False

    def add_token(self, application):
        return self.tokens.create(application=application,
                                  enabled=True)

    def has_address_for_channel(self, channel):
        return self.assignments.filter(channel=channel).exists()

    def send_confirmation_email(self):
        from oath.google_authenticator import from_b32key
        # check = totp(settings.OTP_KEY, period=settings.CONFIRM_EMAIL_EXPIRE)
        gauth = from_b32key(settings.OTP_KEY)
        check = gauth.generate()
        ctx = {
            'user': self,
            'url': absolute_uri(reverse('confirm-registratiom',
                                        args=[self.id, check])
                                ),
            'confirm_email': self.email,
        }
        subject = '[Bitcaster] Confirm Email'

        message = get_template('bitcaster/_emails/confirm_email.txt').render(ctx)
        html_message = get_template('bitcaster/_emails/confirm_email.html').render(ctx)

        ret = send_mail_async(subject=subject,
                              message=message,
                              html_message=html_message,
                              from_email='bitcaster@os4d.org',
                              recipient_list=[self.email])
        return ret

    def store(self, namespace: str, key: str, value):
        try:
            self.storage[namespace][key] = value
        except KeyError:
            self.storage[namespace] = {key: value}
        self.save()

    def retrieve(self, namespace: str, key: str):
        try:
            return self.storage[namespace][key]
        except KeyError:  # pragma: no cover
            return None

    def get_cache_version(self, key):
        return cache.get('user:%s:%s' % (self.pk, key))

    def inc_cache_version(self, key):
        cache.incr('user:%s:%s' % (self.pk, key))
