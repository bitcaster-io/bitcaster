import datetime
import logging
from datetime import timedelta

from celery import chord
from celery.task import periodic_task
from constance import config
from crashlog.models import Error
from django.core.cache import caches
from django.utils import timezone

from bitcaster import system
from bitcaster.celery import app
from bitcaster.models.audit import AuditLogEntry
from bitcaster.models.error import ErrorEntry
from bitcaster.models.notification import Notification
from bitcaster.models.occurence import Occurence
from bitcaster.models.organization import Organization
from bitcaster.tsdb.api import stats

cache_lock = caches['lock']

logger = logging.getLogger(__name__)


@periodic_task(run_every=timedelta(minutes=1), options={'expires': 60})
def clean_data():
    today = timezone.now()
    audit_older_than = today - datetime.timedelta(days=config.LOG_RETENTION_AUDIT)
    events_older_than = today - datetime.timedelta(days=config.LOG_RETENTION_EVENTS)
    errors_older_than = today - datetime.timedelta(days=config.LOG_RETENTION_ERRORS)

    qs = AuditLogEntry.objects.filter(timestamp__lt=audit_older_than)
    qs._raw_delete(qs.db)

    qs = Occurence.objects.filter(timestamp__lt=events_older_than)
    qs._raw_delete(qs.db)

    qs = Notification.objects.filter(timestamp__lt=events_older_than)
    qs._raw_delete(qs.db)

    qs = ErrorEntry.objects.filter(timestamp__lt=errors_older_than)
    qs._raw_delete(qs.db)

    Error.objects.filter(date_time__lt=errors_older_than)
    qs._raw_delete(qs.db)


def _stats(key, **filter):
    Occurence.objects.filter(expire__lt=timezone.now(),
                             status=Occurence.RUNNING,
                             processing__isnull=True,
                             **filter).update(status=Occurence.EXPIRED)

    Notification.objects.filter(occurence__status=Occurence.EXPIRED,
                                status__in=Notification.RUNNING,
                                **filter).update(status=Notification.EXPIRED)

    # terminate all occurences with no pending notifications
    qs = Occurence.objects.filter(status__in=[Occurence.RUNNING],
                                  processing__isnull=True,
                                  **filter).exclude(
        notifications__status__in=Notification.RUNNING)

    qs.update(status=Occurence.TERMINATED)
    # updates queue counters
    pending = Occurence.objects.filter(status__in=Notification.RUNNING,
                                       **filter).count()
    stats.set('occurence:running:%s' % key, pending)

    pending = Notification.objects.filter(occurence__expire__gt=timezone.now(),
                                          status__in=Notification.RUNNING,
                                          **filter).count()
    stats.set('notification:running:%s' % key, pending)

    retry = Notification.objects.filter(occurence__expire__gt=timezone.now(),
                                        status=Notification.RETRY,
                                        **filter).count()
    stats.set('notification:retry:%s' % key, retry)


@periodic_task(run_every=timedelta(minutes=1), options={'expires': 60})
def all_stats():
    for org in Organization.objects.all():
        logger.info('Calculating stats for %s' % org)
        _stats(org.slug, organization=org)


@periodic_task(run_every=timedelta(minutes=1), options={'expires': 60})
def set_notification_status():
    Notification.objects.filter(occurence__expire__lt=timezone.now(),
                                status__in=[Notification.PENDING, Notification.RETRY, Notification.REMIND]
                                ).update(status=Notification.EXPIRED)


@periodic_task(run_every=timedelta(minutes=1), options={'expires': 60})
def consolidate():
    Notification.objects.consolidate()
    ErrorEntry.objects.consolidate()


@periodic_task(run_every=timedelta(minutes=1), options={'expires': 60})
def check_monitors():
    from .monitor import check_monitor, Monitor
    for monitor in Monitor.objects.scheduled():
        check_monitor.delay(monitor.pk)


@app.task(bind=True)
def batch_start(self, result, occurence_pk, *args, **kwargs):
    from bitcaster.models import Occurence
    occurence = Occurence.objects.get(pk=occurence_pk)
    occurence.unlock()


@periodic_task(run_every=timedelta(minutes=1), options={'expires': 60})
def process_notifications():
    from bitcaster.models import Occurence, Notification
    from .event import send_page
    if system.stopped():
        logger.error("Cannot process task 'process_notifications'. LOCKDOWN found")
        return
    for occurence in Occurence.objects.active():
        chord_pages = []
        # lock = cache_lock.lock('occurence:%s' % occurence.pk)
        # if lock.acquire(False):
        if occurence.lock():
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
            chord(chord_pages)(batch_start.s(occurence.pk))
        else:
            occurence.terminate()
