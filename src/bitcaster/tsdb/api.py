from django.conf import settings
from redis import StrictRedis

from bitcaster.models.error import ErrorEntry
from bitcaster.models.notification import Notification
from bitcaster.tsdb.db import TimeSeries

TARGET = ['occurence', 'notification']
TYPES = ['error', 'success']

stats = TimeSeries(StrictRedis.from_url(settings.TSDB_STORE))


def get_data(key, granularity):
    """sss -> TS """
    return stats.get_buckets(key, granularity)


def log_new_occurence(occurence, *args, **kwargs):
    stats.increase('occurence')
    stats.add('occurence')


def log_occurence_error(event, *args, **kwargs):
    pass


def log_new_notifications(channel_pk, page_size, *args, **kwargs):
    stats.add('notification', page_size)


def log_sent_notification(notification, *args, **kwargs):
    stats.rm('notification', 1)
    stats.increase('notification')
    notification.status = Notification.COMPLETE
    notification.save()


def log_error_event(event, message='Error', *args, **kwargs):
    ErrorEntry.objects.create(message=message % dict(event=event),
                              application=None,
                              target=event,
                              data=kwargs).consolidate()
    stats.add('event:%s' % event.pk, type='error')


def log_error_channel(channel, message='Error', *args, **kwargs):
    ErrorEntry.objects.create(message=message % dict(channel=channel),
                              application=None,
                              target=channel,
                              data=kwargs).consolidate()
    stats.add('channel:%s' % channel.pk, type='error')


def log_error_occurence(occurence, message='Error', *args, **kwargs):
    ErrorEntry.objects.create(message=message,
                              application=None,
                              target=occurence,
                              data=kwargs).consolidate()
    stats.add('occurence', type='error')
    stats.add('occurence:%s' % occurence.pk, type='error')
    stats.add('event:%s' % occurence.event.pk, type='error')


def log_error_notification(notification: Notification, message='Error', *args, **kwargs):
    kwargs.update({'channel': str(notification.channel),
                   'address': str(notification.address),
                   'subscription': str(notification.subscription),
                   })
    ErrorEntry.objects.create(message=message,
                              application=None,
                              target=notification,
                              data=kwargs).consolidate()
    notification.status = Notification.RETRY
    notification.save()
    stats.add('notification', type='error')
    stats.add('notification:%s' % notification.pk, type='error')
