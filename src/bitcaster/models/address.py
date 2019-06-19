import logging
import string

from django.conf import settings
from django.db import models

from bitcaster.models.mixins import ReverseWrapperMixin, ReversionMixin
from bitcaster.utils.reflect import fqn
from bitcaster.utils.strings import random_string

from .channel import Channel

logger = logging.getLogger(__name__)


class AddressQuerySet(models.QuerySet):
    def unlocked(self, *args, **kwargs):
        return self.filter(locked=False).filter(*args, **kwargs)

    def locked(self, *args, **kwargs):
        return self.filter(locked=True).filter(*args, **kwargs)


class AddressAssignmentQuerySet(models.QuerySet):
    def unverified(self, *args, **kwargs):
        return self.unlocked(verified=False).filter(*args, **kwargs)

    def unlocked(self, *args, **kwargs):
        return self.filter(locked=False).filter(*args, **kwargs)

    def locked(self, *args, **kwargs):
        return self.filter(locked=True).filter(*args, **kwargs)

    def get_address(self, klass):
        try:
            return self.filter(verified=True).get(channel__handler=fqn(klass)).address
        except Exception:
            raise AddressAssignment.DoesNotExist('Cannot find valid any address for %s' % fqn(klass))


class Address(ReversionMixin, ReverseWrapperMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='addresses',
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    label = models.CharField(max_length=50)
    locked = models.BooleanField(default=False)
    channels = models.ManyToManyField(Channel,
                                      through='bitcaster.AddressAssignment',
                                      blank=True)

    objects = AddressQuerySet.as_manager()

    class Meta:
        unique_together = (('user', 'label'),)
        app_label = 'bitcaster'
        ordering = 'label',

    def __str__(self):
        return self.label

    def __init__(self, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)
        self.__original_address = self.address

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        if self.address != self.__original_address:
            self.assignments.update(verified=False)
            self.__original_address = self.address
            self.user.subscriptions.filter(assignment__address=self).update(enabled=False)


class AddressAssignment(ReversionMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='assignments',
                             on_delete=models.CASCADE)
    address = models.ForeignKey(Address,
                                related_name='assignments',
                                on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel,
                                related_name='assignments',
                                on_delete=models.CASCADE)

    code = models.CharField(null=True, max_length=9)
    locked = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    objects = AddressAssignmentQuerySet.as_manager()

    class Meta:
        app_label = 'bitcaster'
        unique_together = ('user', 'address', 'channel')

    def __str__(self):
        return '%s (%s)' % (self.channel.name, self.address.label)

    def code_is_valid(self, code):
        if code and self.code == code:
            self.verified = True
            self.save()
        return self.verified

    def send_verification_code(self):
        self.code = random_string(6, string.digits)
        self.save()
        return self.channel.handler.emit(self.address.address,
                                         'Bitcaster confirmation code',
                                         'Bitcaster confirmation code %s' % self.code,
                                         silent=False)
