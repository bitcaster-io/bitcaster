import datetime
from datetime import timedelta

from celery import chord
from celery.task import periodic_task
from crashlog.models import Error
from django.core.cache import caches
from django.utils import timezone

from bitcaster.celery import app
from bitcaster.models.error import ErrorEntry
from bitcaster.models.notification import Notification
from bitcaster.models.occurence import Occurence
from bitcaster.tsdb.api import stats

cache_lock = caches['lock']


@periodic_task(run_every=timedelta(minutes=1))
def clean_data():
    today = timezone.now()
    older_than = today - datetime.timedelta(days=30)
    qs = Occurence.objects.filter(timestamp__lt=older_than)
    qs._raw_delete(qs.db)

    qs = Notification.objects.filter(timestamp__lt=older_than)
    qs._raw_delete(qs.db)


@periodic_task(run_every=timedelta(minutes=1))
def set_occurences_status():
    # check for expired occurences
    Occurence.objects.filter(expire__lt=timezone.now(),
                             status=Occurence.RUNNING).update(status=Occurence.EXPIRED)

    # terminate all occurences with no pending notifications
    # closed = Notification.objects.filter(status__in=[Notification.EXPIRED,
    #                                                  Notification.COMPLETE]).distinct().values_list('occurence',
    #                                                                                                 flat=True)
    #
    # Occurence.objects.filter(id__in=closed, status=Occurence.RUNNING).update(status=Occurence.TERMINATED)

    qs = Occurence.objects.filter(status__in=[Occurence.RUNNING]).exclude(
        notifications__status__in=[Notification.PENDING,
                                   Notification.REMIND,
                                   Notification.RETRY])

    qs.update(status=Occurence.TERMINATED)

    # updates queue counters
    pending = Occurence.objects.exclude(status__in=[Notification.EXPIRED,
                                                    Notification.CONFIRMED,
                                                    Notification.COMPLETE]).count()
    stats.set('occurence', pending)

    pending = Notification.objects.filter(occurence__expire__gt=timezone.now(),
                                          status__in=[Notification.PENDING,
                                                      Notification.RETRY]).count()
    stats.set('notification', pending)

    retry = Notification.objects.filter(occurence__expire__gt=timezone.now(),
                                        status=Notification.REMIND).count()
    stats.set('notification:retry', retry)


@periodic_task(run_every=timedelta(minutes=1))
def set_notification_status():
    Notification.objects.filter(occurence__expire__lt=timezone.now(),
                                status__in=[Notification.PENDING, Notification.RETRY, Notification.REMIND]
                                ).update(status=Notification.EXPIRED)


@periodic_task(run_every=timedelta(days=30))
def clean_errors():
    Error.objects.filter(date_time__lte=datetime.datetime.today() - datetime.timedelta(days=30)).delete()


@periodic_task(run_every=timedelta(minutes=1))
def consolidate():
    Notification.objects.consolidate()
    ErrorEntry.objects.consolidate()


@app.task(bind=True)
def callback(self, result, occurence_pk, *args, **kwargs):
    lock = cache_lock.lock('occurence:%s' % occurence_pk)
    cache_lock.delete(lock.name)


@periodic_task(bind=True, run_every=timedelta(minutes=1))
def check_monitors(self):
    from .monitor import check_monitor, Monitor
    for monitor in Monitor.objects.filter(enabled=True):
        check_monitor.delay(monitor.pk)


@periodic_task(bind=True, run_every=timedelta(minutes=1))
def process_notifications(self):
    from bitcaster.models import Occurence, Notification
    from .event import send_page

    if cache_lock.get('STOP'):
        return

    for occurence in Occurence.objects.active():
        chord_pages = []
        lock = cache_lock.lock('occurence:%s' % occurence.pk)
        if lock.acquire(False):
            print(f'Processing occurence {occurence}')

            for channel in occurence.event.channels.all():
                partition = channel.dispatch_page_size
                page = []
                filters = dict(channel=channel,
                               occurence=occurence,
                               next_sent__lt=timezone.now())
                for notification in Notification.objects.pending().filter(**filters):
                    page.append(notification.pk)
                    if len(page) == partition:
                        chord_pages.append(send_page.s(occurence.pk, channel.pk, page))
                        page = []

                if page:
                    chord_pages.append(send_page.s(occurence.pk, channel.pk, page))
        else:
            print(f'Cannot process {occurence}. Lock found')

        if chord_pages:
            chord(chord_pages)(callback.s(occurence.pk))
