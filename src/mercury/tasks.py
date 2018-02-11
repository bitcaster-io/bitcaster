# -*- coding: utf-8 -*-
import datetime

from django.template import Template, Context

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
    event.emit(context)


@app.task()
def emit_event(self, context):
    from mercury.models.message import Message
    logger.debug("Event [{0.name}] emit()".format(self))
    errored_channels = []
    success = 0
    failure = 0
    if not self.enabled:
        raise LogicError("Cannot emit disabled event")

    for subscription in self.subscriptions.valid():
        if subscription.channel not in errored_channels:
            try:
                ctx = dict(context or {})
                ctx.update({
                    'recipient': subscription.subscriber,
                    'today': datetime.datetime.today()})
                message = self.get_message(subscription.channel)
                body = Template(message.body).render(Context(ctx))
                subject = Template(message.subject).render(Context(ctx))
                subscription.channel.send(subscription,
                                          subject, body)
                success += 1
            except Message.DoesNotExist as e:
                logger.exception(e)
                errored_channels.append(subscription.channel)
                subscription.channel.enabled = False
                subscription.channel.save()
                failure += 1
            except Exception as e:
                logger.exception(e)
                failure += 1
            else:
                logger.debug(f"Subscription {subscription.pk} emit successful")
        else:
            logger.debug("Event [{0.name}] emit skipped because channel misconfiguration".format(self))

    return success, failure
