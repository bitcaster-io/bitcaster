from constance import config
from django.contrib.postgres.fields import JSONField
from django.db import models


class Notification(models.Model):
    MESSAGE_NONE = 0
    MESSAGE_TPL = 1
    MESSAGE_ARG = 2
    MESSAGE_ALL = 3
    MESSAGE_POLICIES = ((MESSAGE_NONE, 'None'),
                        (MESSAGE_TPL, 'Template'),
                        (MESSAGE_ARG, 'Arguments'),
                        (MESSAGE_ALL, 'Full message'))

    timestamp = models.DateTimeField(auto_now_add=True)
    # organization = models.ForeignKey('bitcaster.Organization',
    #                                 related_name='+',
    #                                 on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    related_name='+',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('bitcaster.Event',
                              related_name='+',
                              null=True,
                              on_delete=models.SET_NULL)
    subscription = models.ForeignKey('bitcaster.Subscription',
                                     null=True,
                                     related_name='+',
                                     on_delete=models.SET_NULL)
    user = models.ForeignKey('bitcaster.User',
                             null=True,
                             related_name='+',
                             on_delete=models.SET_NULL)
    channel = models.ForeignKey('bitcaster.Channel',
                                null=True,
                                related_name='+',
                                on_delete=models.SET_NULL)

    address = models.CharField(max_length=200, null=True, blank=True)
    event_name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)

    status = models.BooleanField(help_text='True if successed', default=True)
    info = models.TextField(null=True, blank=True)
    data = JSONField(null=True, blank=True)

    class Meta:
        app_label = 'bitcaster'

    @classmethod
    def log(cls, address: str, subscription, payload, **kwargs):
        if config.LOG_MESSAGE == cls.MESSAGE_ALL:
            data = payload
        elif config.LOG_MESSAGE == cls.MESSAGE_TPL:
            data = payload
        elif config.LOG_MESSAGE == cls.MESSAGE_TPL:
            data = payload
        else:
            data = {}

        values = dict(event=subscription.event,
                      event_name=subscription.event.name,
                      address=address or '-',
                      channel=subscription.channel,
                      data=data,
                      user=subscription.subscriber,
                      username=subscription.subscriber.email,
                      subscription=subscription,
                      application=subscription.event.application,
                      status=True)
        values.update(kwargs)
        cls.objects.create(**values)
