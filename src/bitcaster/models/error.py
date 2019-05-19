from enum import IntEnum

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ErrorEvent(IntEnum):
    SUBSCRIPTION_ERROR = 100
    CHANNEL_ERROR = 200


MESSAGES = {
    ErrorEvent.SUBSCRIPTION_ERROR: _('%()s'),
}


class ErrorEntry(models.Model):
    ERROREVENT_CHOICES = [(tag.value, tag.name) for tag in ErrorEvent]
    event = models.IntegerField(choices=ERROREVENT_CHOICES)

    organization = models.ForeignKey('bitcaster.Organization',
                                     related_name='errors',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    blank=True, null=True,
                                    related_name='errors',
                                    on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('content_type', 'object_id')
    target_label = models.CharField(max_length=300, null=True, blank=True)

    data = JSONField(blank=True, null=True)

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ('timestamp',)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        # if self.application:
        #     self.organization = self.application.organization
        # elif not self.application and hasattr(self.target, 'application'):
        #     self.application = self.target.application
        #
        if self.target and hasattr(self.target, 'application'):
            self.application = self.target.application
        elif self.target and hasattr(self.target, 'event'):
            self.application = self.target.event.application

        if self.application:
            self.organization = self.application.organization
        # if not self.organization and hasattr(self.target, 'organization'):
        #     self.organization = self.target.organization
        super().save(force_insert, force_update, using, update_fields)
