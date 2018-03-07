# -*- coding: utf-8 -*-
from constance import config
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import Count

from mercury.celery import app
from mercury.exceptions import LogicError
from mercury.logging import getLogger

logger = getLogger(__name__)

app.conf.beat_schedule = {
    'add-every-60-seconds': {
        'task': 'mercury.tasks.beat',
        'schedule': 60.0,
        # 'args': (1,)
    },
}


@app.task()
def trigger_event(event_id, context):
    from mercury.models import Event
    event = Event.objects.get(id=event_id)
    emit_event(event, context)


def emit_event(event, context, ignore_disabled=False):
    from mercury.models import Channel
    from mercury.models.counters import Counter, Occurence

    logger.debug("Event [{0.name} {0.enabled}] emit()".format(event))
    total_success = 0
    total_failure = 0
    if not event.enabled and not ignore_disabled:
        raise LogicError("Cannot emit disabled event")
    channels = event.subscriptions.valid().values('channel').annotate(dcount=Count('channel'))
    ids = [channel['channel'] for channel in channels]
    if len(channels) == 0:
        logger.warning(f"No subscriptions/channels found for `{event}`")
    o = Occurence.objects.create(event=event)
    Counter.objects.initialize(event)
    for channel in Channel.objects.filter(id__in=ids, enabled=True):
        try:
            logger.debug(f"Processing channel {channel}")
            success, failure = channel.process_event(event, context)
            total_success += success
            Counter.objects.increment(event)
        except Exception as e:
            logger.exception(e)
            total_failure += 1
    o.submissions = total_failure + total_success
    o.successes = total_success
    o.failures = total_failure
    o.save()
    logger.debug(f"End processing {event}. #{o.submissions} messages sent")
    return total_success, total_failure


@app.task()
def send_mail_async(subject, message, html_message, recipient_list,
                    *,
                    from_email=None,
                    fail_silently=False):
    connection = get_connection(
        fail_silently=fail_silently,
        username=config.EMAIL_HOST_USER,
        password=config.EMAIL_HOST_PASSWORD,
        use_tls=config.EMAIL_USE_TLS,
        host=config.EMAIL_HOST,
        port=config.EMAIL_HOST_PORT,
        timeout=config.EMAIL_TIMEOUT
    )
    mail = EmailMultiAlternatives(subject, message,
                                  from_email,
                                  recipient_list,
                                  connection=connection)
    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    return mail.send()
