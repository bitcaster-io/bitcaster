import logging
import string

from django.conf import settings
from django.db import models
from strategy_field.fields import MultipleStrategyField

from bitcaster.dispatchers import dispatcher_registry
from bitcaster.models.mixins import ReversionMixin
from bitcaster.utils.reflect import fqn
from bitcaster.utils.strings import random_string

from .channel import Channel

logger = logging.getLogger(__name__)


class AssignmentQuerySet(models.QuerySet):
    def get_address(self, klass):
        try:
            return self.filter(address__verified=True).get(channel__handler=fqn(klass)).address
        except Exception:
            raise Address.DoesNotExist('Cannot find valid any address for %s' % fqn(klass))


class Address(ReversionMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='addresses',
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    label = models.CharField(max_length=50)

    verified = models.BooleanField(default=False)
    code = models.CharField(null=True, max_length=9)
    locked = models.BooleanField(default=False)
    valid_for = MultipleStrategyField(registry=dispatcher_registry,
                                      blank=True, null=True)

    class Meta:
        unique_together = (('user', 'label'),)
        app_label = 'bitcaster'

    def __str__(self):
        return self.label

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__address = str(self.address)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk and (self.address != self.__address):
            self.verified = False
            self.code = random_string(8, string.digits)
        super().save(force_insert, force_update, using, update_fields)


class AddressAssignment(ReversionMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='assignments',
                             on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='used_by')
    channel = models.ForeignKey(Channel,
                                on_delete=models.CASCADE,
                                related_name='addresses')

    objects = AssignmentQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'channel',),
        app_label = 'bitcaster'

    def __str__(self):
        return str(self.address)

    def code_is_valid(self, code):
        if code and self.address.code == code:
            self.address.verified = True
            self.address.save()
        return self.address.verified

    def send_verification_code(self):
        address = self.address
        code = random_string(6, string.digits)
        address.code = code
        address.save()
        return self.channel.handler.emit(self.address.address,
                                         'Bitcaster confirmation code',
                                         'Bitcaster confirmation code %s' % code,
                                         silent=False)
