from django.db import models
from django.utils import timezone

from bitcaster.framework.db.fields import EncryptedPickledObjectField


class AbstractOption(models.Model):
    key = models.CharField(max_length=64, unique=True)
    value = EncryptedPickledObjectField()
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'bitcaster'
        abstract = True


class Option(AbstractOption):
    pass


class OrganizationOption(AbstractOption):
    organization = models.ForeignKey('bitcaster.Organization',
                                     related_name='options',
                                     on_delete=models.CASCADE)
