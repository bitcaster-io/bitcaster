import datetime
from datetime import timedelta

from celery import chord
from celery.task import periodic_task
from crashlog.models import Error
from django.utils import timezone

from bitcaster.celery import app
from bitcaster.models.error import ErrorEntry
from bitcaster.models.notification import Notification
from bitcaster.models.occurence import Occurence
from bitcaster.tsdb.api import stats


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
                                                    Notification.COMPLETE]).count()
    stats.set('occurence', pending)

    pending = Notification.objects.filter(occurence__expire__gt=timezone.now(),
                                          status__in=[Notification.PENDING,
                                                      Notification.REMIND,
                                                      Notification.RETRY]).count()
    stats.set('notification', pending)


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
def callback(self, *args, **kwargs):
    pass


@periodic_task(bind=True, run_every=timedelta(minutes=1))
def process_notifications(self):
    from bitcaster.models import Occurence, Notification
    from .event import send_page

    for occurence in Occurence.objects.active():
        chord_pages = []

        for channel in occurence.event.channels.all():
            partition = channel.dispatch_page_size
            page = []
            for notification in Notification.objects.pending().filter(channel=channel,
                                                                      occurence=occurence):
                page.append(notification.pk)
                if len(page) == partition:
                    chord_pages.append(send_page.s(channel.pk, occurence.pk, page))
                    page = []

            if page:
                chord_pages.append(send_page.s(channel.pk, occurence.pk, page))

            if chord_pages:
                chord(chord_pages)(callback.s())
