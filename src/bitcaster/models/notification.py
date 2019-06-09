import base64
from io import BytesIO

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext as _

from bitcaster.attachments.base import Attachment
from bitcaster.framework.db.fields import EncryptedJSONField


class NotificationManager(models.Manager):
    def consolidate(self):
        for entry in self.filter(organization__isnull=True):
            entry.event = entry.subscription.event
            entry.application = entry.event.application
            entry.organization = entry.application.organization
            entry.user = entry.subscription.subscriber
            entry.save()

    def pending(self, **kwargs):
        return self.filter(status__in=[Notification.PENDING,
                                       Notification.RETRY,
                                       Notification.REMIND],
                           **kwargs)

    def missed(self, **kwargs):
        return self.filter(status__in=[Notification.EXPIRED,
                                       Notification.WAIT],
                           **kwargs)


def parse_attachment(attachment_string):
    c = base64.b64decode(attachment_string['content'])
    return Attachment(attachment_string['name'],
                      BytesIO(c),
                      attachment_string['content_type'])


class AttachmentField(EncryptedJSONField):
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        value = super().from_db_value(value, expression, connection, context)
        return parse_attachment(value)

    def get_prep_value(self, value):
        c = value.content.read()
        return super().get_prep_value(dict(name=value.name,
                                           content=base64.b64encode(c).decode(),
                                           content_type=value.content_type))

    def to_python(self, value):
        if isinstance(value, Attachment):
            return value

        if value is None:
            return value

        return parse_attachment(value)


class Notification(models.Model):
    PENDING = 0  # Queued no sending happened
    RETRY = 20  # Sent failed retrying
    REMIND = 21  # Reminder scheduled
    WAIT = 22

    WRONG_ADDRESS = 98
    EXPIRED = 99
    CONFIRMED = 101  # confirmation received / or single successful sent with no confirmations
    COMPLETE = 100  # confirmation received / or single successful sent with no confirmations

    STATUSES = ((PENDING, _('Pending')),
                (RETRY, _('Retry')),
                (REMIND, _('Remind')),
                (WAIT, _('Waiting confirmation')),
                (WRONG_ADDRESS, _('Address not confirmed')),
                (EXPIRED, _('Expired')),
                (COMPLETE, _('Complete')),
                (CONFIRMED, _('Confirmed')),
                )
    RUNNING = [PENDING, RETRY, REMIND, WAIT]
    NOT_RUNNING = [WRONG_ADDRESS, EXPIRED, CONFIRMED, COMPLETE]

    MESSAGE_NONE = 0
    MESSAGE_TPL = 1
    MESSAGE_ARG = 2
    MESSAGE_ALL = 3
    MESSAGE_POLICIES = ((MESSAGE_NONE, 'None'),
                        (MESSAGE_TPL, 'Template'),
                        (MESSAGE_ARG, 'Arguments'),
                        (MESSAGE_ALL, 'Full message'))

    timestamp = models.DateTimeField(auto_now_add=True)
    subscription = models.ForeignKey('bitcaster.Subscription',
                                     null=True,
                                     related_name='+',
                                     on_delete=models.SET_NULL)
    address = models.CharField(max_length=200, null=True, blank=True)
    event_name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)

    success = models.BooleanField(help_text='True if successed', default=True)
    info = models.TextField(null=True, blank=True)
    data = EncryptedJSONField(null=True, blank=True)

    development_mode = models.BooleanField(default=False)
    # post processed
    organization = models.ForeignKey('bitcaster.Organization',
                                     null=True, blank=True,
                                     related_name='+',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    null=True, blank=True,
                                    related_name='+',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('bitcaster.Event',
                              null=True, blank=True,
                              related_name='+',
                              on_delete=models.SET_NULL)
    user = models.ForeignKey('bitcaster.User',
                             null=True, blank=True,
                             related_name='notifications',
                             on_delete=models.SET_NULL)
    channel = models.ForeignKey('bitcaster.Channel',
                                null=True, blank=True,
                                related_name='+',
                                on_delete=models.SET_NULL)

    occurence = models.ForeignKey('bitcaster.Occurence',
                                  null=True, blank=True,
                                  db_index=True,
                                  related_name='notifications',
                                  on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUSES, default=PENDING, db_index=True)
    retry_scheduled = models.BooleanField(default=False)
    next_sent = models.DateTimeField(blank=True, null=True)

    need_confirmation = models.BooleanField(default=False)
    confirmed = models.DateTimeField(default=None, blank=True, null=True)

    max_reminders = models.IntegerField(blank=True, null=True)
    reminders = models.IntegerField(default=1, blank=True, null=True)
    reminders_timestamps = models.TextField(blank=True, null=True)

    attachments = ArrayField(AttachmentField(), blank=True, null=True)

    objects = NotificationManager()

    class Meta:
        app_label = 'bitcaster'
        unique_together = ('channel', 'occurence', 'address')
