# -*- coding: utf-8 -*-
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
            channel.validate_config()
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

    # for subscription in event.subscriptions.valid():
    #     if subscription.channel not in errored_channels:
    #         try:
    #             ctx = dict(context or {})
    #             ctx.update({
    #                 'recipient': subscription.subscriber,
    #                 'today': datetime.datetime.today()})
    #             message = event.get_message(subscription.channel)
    #             body = Template(message.body).render(Context(ctx))
    #             subject = Template(message.subject).render(Context(ctx))
    #             subscription.channel.send(subscription,
    #                                       subject, body)
    #             success += 1
    #         except Message.DoesNotExist as e:
    #             logger.exception(e)
    #             errored_channels.append(subscription.channel)
    #             subscription.channel.enabled = False
    #             subscription.channel.save()
    #             failure += 1
    #         except Exception as e:
    #             logger.exception(e)
    #             failure += 1
    #         else:
    #             logger.debug(f"Subscription {subscription.pk} emit successful")
    #     else:
    #         logger.debug("Event [{0.name}] emit skipped because channel misconfiguration".format(event))
    #
    # return success, failure
