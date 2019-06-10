from enum import IntEnum

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bitcaster.tasks.model import async


class ErrorEvent(IntEnum):
    SUBSCRIPTION_ERROR = 100
    CHANNEL_ERROR = 200


MESSAGES = {
    ErrorEvent.SUBSCRIPTION_ERROR: _('%()s'),
}


class ErrorEntryManager(models.Manager):
    def consolidate(self):
        for e in self.filter(organization__isnull=True):
            e.consolidate(async=False)


class ErrorEntry(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)

    actor_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    actor_object_id = models.PositiveIntegerField(null=True, blank=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    target_content_type = models.ForeignKey(ContentType, related_name='+',
                                            on_delete=models.CASCADE, null=True,
                                            blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    data = JSONField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    actor_label = models.CharField(max_length=300, null=True, blank=True)
    target_label = models.CharField(max_length=300, null=True, blank=True)
    organization = models.ForeignKey('bitcaster.Organization',
                                     blank=True, null=True,
                                     related_name='errors',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    blank=True, null=True,
                                    related_name='errors',
                                    on_delete=models.CASCADE)

    objects = ErrorEntryManager()

    class Meta:
        get_latest_by = 'timestamp'
        ordering = ('timestamp',)
        app_label = 'bitcaster'

    @async(quque='consolidate')
    def consolidate(self):
        if hasattr(self.actor, 'application'):
            self.application = self.actor.application
        elif hasattr(self.actor, 'event'):
            self.application = self.actor.event.application

        if self.application:
            self.organization = self.application.organization

        self.actor_label = str(self.actor)
        self.target_label = str(self.target)
        self.save()
    # @classmethod
    # def log(cls, target, **kwargs):
    #     return ErrorEntry.objects.create(target=target, **kwargs)
    #
    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     # if self.application:
    #     #     self.organization = self.application.organization
    #     # elif not self.application and hasattr(self.target, 'application'):
    #     #     self.application = self.target.application
    #     #
    #     if self.target and hasattr(self.target, 'application'):
    #         self.application = self.target.application
    #     elif self.target and hasattr(self.target, 'event'):
    #         self.application = self.target.event.application
    #
    #     if self.application:
    #         self.organization = self.application.organization
    #     # if not self.organization and hasattr(self.target, 'organization'):
    #     #     self.organization = self.target.organization
    #     super().save(force_insert, force_update, using, update_fields)
