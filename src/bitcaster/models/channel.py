import logging

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from bitcaster.framework.db.fields import DispatcherField, EncryptedJSONField
from bitcaster.models.fields import ThrottleField
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

    def selectable(self, application, **kwargs):
        return self.filter(Q(organization=application.organization) |
                           Q(system=True) |
                           Q(application=application)).filter(**kwargs)


def set_error(value, error):
    return value


class Channel(ReverseWrapperMixin, AbstractModel):
    """ A Channel represent a configured dispatcher. """
    name = models.CharField(_('name'), max_length=255)
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
    enabled = models.BooleanField(_('enabled'),
                                  default=False)
    description = models.TextField(_('description'),
                                   blank=True, null=True)
    handler = DispatcherField(null=True)
    deprecated = models.BooleanField(default=False)

    errors_threshold = models.IntegerField(default=100,
                                           help_text='Number or errors before channel will be automatically disabled')
    objects = ChannelQuerySet().as_manager()

    dispatch_page_size = models.IntegerField(_('dispatcher page size'),
                                             validators=[MinValueValidator(1)],
                                             default=1000)
    dispatch_rate = ThrottleField(_('dispatch rate'),
                                  default='1/s')

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
    #
    # @property
    # def errors(self):
    #     try:
    #         return counters.get_buckets('channel:%s:errors' % self.pk, 'd', 1)[0][1]
    #     except Exception as e:
    #         logger.exception(e)
    #         return 0
    #
    # def register_error(self, **kwargs):
    #     ErrorEntry.objects.create(event=ErrorEvent.CHANNEL_ERROR,
    #                               application=None,
    #                               organization=self.organization,
    #                               target=self,
    #                               data=kwargs)
    #     counters.increase('channel:%s:errors' % self.pk)
    #     return self.errors
