import datetime
from logging import getLogger

from constance import config
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import Count
from django.template import Template

from bitcaster.celery import app
from bitcaster.exceptions import LogicError, MaxChannelError
from bitcaster.logging import log_notification, log_occurence
from bitcaster.template.secure_context import SecureContext

logger = getLogger(__name__)


@app.task()
def trigger_event(event_id, context, *, token=None, origin=None):
    from bitcaster.models import Event
    event = Event.objects.get(id=event_id)
    emit_event(event, context)


@app.task()
def process_channel(event_pk, channel_pk):
    pass


def emit_event(event, context, ignore_disabled=False):
    from bitcaster.models import Channel, Counter, DispatcherMetaData
    logger.debug('Event [{0.name} {0.enabled}] emit()'.format(event))
    total_success = 0
    total_failure = 0
    if not event.enabled and not ignore_disabled:
        raise LogicError('Cannot emit disabled event')
    channels = event.subscriptions.valid().values('channel').annotate(dcount=Count('channel'))
    ids = [channel['channel'] for channel in channels]
    if len(channels) == 0:
        logger.warning(f'No subscriptions/channels found for `{event}`')
    # o = Occurence.objects.create(event=event, token=token, origin=origin)
    # Counter.objects.initialize(event)
    for channel in Channel.objects.filter(id__in=ids, enabled=True):
        if not DispatcherMetaData.objects.get(handler=channel.handler).enabled:
            logger.error("Channel '%s' is using a disabled dispatcher" % channel)
            continue
        try:
            logger.debug(f'Processing channel {channel}')
            successes, failures = channel.process_event(event, context)
            total_success += successes
            total_failure += failures
            Counter.objects.increment(event)
        except Exception as e:
            logger.exception(e)
            total_failure += 1
    log_occurence(event, submissions=total_failure + total_success,
                  successes=total_success,
                  failures=total_failure)
    # o.submissions = total_failure + total_success
    # o.successes = total_success
    # o.failures = total_failure
    # o.save()
    # logger.debug(f'End processing {event}. #{o.submissions} messages sent')
    return total_success, total_failure


def process_event(channel, event, context):
    if not channel.enabled:
        logger.error('Channel {0} disabled'.format(channel))
        return 0, 0
    try:
        message = channel.messages.get(event=event)
        body = Template(message.body)
        subject = Template(message.subject)
        # state.data['event'] = event
        # logger.debug(f"Processing event {event}")
        conn = channel.handler._get_connection()
        success, failures = 0, 0
        logging_kwargs = {}
        for subscription in event.subscriptions.valid(channel=channel):
            # state.data['subscription'] = subscription
            logger.debug(f'Processing {subscription}')
            try:
                ctx = dict(context or {})
                ctx.update({
                    'event': event,
                    'channel': channel,
                    'application': channel.application,
                    'organization': channel.organization,
                    'subscription': subscription,
                    'recipient': subscription.subscriber,
                    'today': datetime.datetime.today()})
                m = body.render(SecureContext(ctx))
                s = subject.render(SecureContext(ctx))
                logging_kwargs.update(message=m,
                                      subject=s,
                                      context=ctx,
                                      template=body)
                # address
                used_address = channel.handler.emit(subscription, s, m, conn)
                logging_kwargs['address'] = used_address
                # Counter.objects.increment(subscription)
                success += 1
                # Notification.log(address, subscription, payload)
            except Exception as e:
                logging_kwargs['error'] = e
                subscription.register_error()
                channel.register_error()
                logger.exception(e)
                # Notification.log('', subscription, payload, status=False, info=str(e))
                failures += 1

            log_notification(subscription, **logging_kwargs)

            if failures >= channel.errors_threshold:
                raise MaxChannelError(channel)
    except MaxChannelError as e:
        logger.error(e)
        channel.enabled = False
        channel.save()
        raise
    except ObjectDoesNotExist as e:
        logger.error(e)
        raise ObjectDoesNotExist(f'Unable to find a message for {channel}/{event}') from e
    except Exception as e:
        logger.exception(e)
        raise

    return success, failures


@app.task()
def send_mail_async(subject, message, html_message, recipient_list,
                    *,
                    from_email=None,
                    fail_silently=False):
    try:
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
        sent = mail.send()
        assert sent == 1
        logger.debug(f"Email '{subject}' sent to {recipient_list}")
        return sent
    except Exception as e:
        logger.exception(e)
        raise
