import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from sentry_sdk import capture_exception

from bitcaster.exceptions import PluginValidationError
from bitcaster.framework.db.fields import DispatcherField, EncryptedJSONField
from bitcaster.models.error import ErrorEntry, ErrorEvent
from bitcaster.models.mixins import ReverseWrapperMixin

from .application import Application
from .base import AbstractModel
from .organization import Organization

logger = logging.getLogger(__name__)


class ChannelQuerySet(models.QuerySet):
    def valid(self):
        # for c in self.all():
        #     try:
        #         assert c.handler
        #     except Exception:
        #         c.handler = None
        #         c.enabled = False
        #         c.save()
        return self.all()

    def selectable(self, application):
        return self.filter(Q(organization=application.organization) |
                           Q(system=True) |
                           Q(application=application))


class Channel(ReverseWrapperMixin, AbstractModel):
    """ A Channel represent a configured dispatcher. """
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization,
                                     null=True,
                                     blank=True,
                                     related_name='channels',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey(Application,
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE)
    system = models.BooleanField(default=False)
    config = EncryptedJSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    handler = DispatcherField(null=True)
    deprecated = models.BooleanField(default=False)

    errors = models.PositiveIntegerField(default=0)
    errors_threshold = models.IntegerField(default=100,
                                           help_text='Number or errors before channel will be automatically disabled')
    objects = ChannelQuerySet().as_manager()

    class Meta:
        app_label = 'bitcaster'
        ordering = ('organization', 'application', 'name')
        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')

    class Reverse:
        pattern = 'org-channel-{op}'
        args = ['organization.slug', 'id']

    def __repr__(self):
        return f'<Channel #{self.id} {self.name}>'

    def __str__(self):
        return self.name

    def validate_address(self, address):
        return self.handler.validate_address(address)

    def validate_subscription(self, subscription):
        try:
            return self.handler.validate_subscription(subscription)
        except Exception as e:
            capture_exception()
            raise PluginValidationError() from e

    def validate_message(self, message, **kwargs):
        """
        :param message models.Message instance:
        :param kwargs:
        :return:
        """
        self.handler.validate_message(message, **kwargs)

    def get_usage_message(self):
        return self.handler.get_usage_message()

    def get_usage(self):
        return self.handler.get_usage()

    @property
    def is_configured(self):
        if self.handler:
            return self.handler.validate_configuration(self.config, False)
        return False

    def clean(self):
        if not self.handler and self.enabled:
            raise ValidationError('Cannot enable Channel without handler')
        if self.enabled:
            if not self.is_configured:
                raise ValidationError('Configure channel before enable it')

    def register_error(self):
        ErrorEntry.objects.create(event=ErrorEvent.SUBSCRIPTION_ERROR, target=self)
        self.errors += 1
        self.save()
        return self.errors
