import datetime
from logging import getLogger

from crashlog.middleware import process_exception
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.template import Template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from sentry_sdk import capture_exception

from bitcaster.celery import app
from bitcaster.exceptions import LogicError
from bitcaster.template.secure_context import SecureContext
from bitcaster.tsdb.api import (log_error_channel, log_error_event,
                                log_error_notification, log_error_occurence,
                                log_new_notifications, log_sent_notification,)
from bitcaster.utils.http import absolute_uri

logger = getLogger(__name__)


@app.task()
def trigger_event(occurence_id, context, *, token=None, origin=None):
    from bitcaster.models import Channel, DispatcherMetaData, Occurence
    occurence = Occurence.objects.select_related('event').get(id=occurence_id)
    event = occurence.event
    logger.debug('Event [{0.name} {0.enabled}] emit()'.format(event))
    if not event.enabled:
        log_error_occurence(occurence)
        raise LogicError('Cannot emit disabled event')
    channels = event.subscriptions.valid().values('channel').annotate(dcount=Count('channel'))
    ids = [channel['channel'] for channel in channels]
    if len(channels) == 0:
        logger.warning(f'No subscriptions/channels found for `{event}`')
    for channel in Channel.objects.filter(id__in=ids,
                                          event=event,
                                          enabled=True):
        if not channel.enabled:
            log_error_channel(channel, "Channel '%(channel)s' is disabled")
            # channel.register_error("Channel '%s' is disabled" % channel)
            logger.error("Channel '%s' is disabled" % channel)
            continue
        if not DispatcherMetaData.objects.get(handler=channel.handler).enabled:
            log_error_channel(channel, "Channel '%(channel)s' is using a disabled dispatcher")
            # channel.register_error("Channel '%s' is using a disabled dispatcher" % channel)
            logger.error("Channel '%s' is using a disabled dispatcher" % channel)
            continue
        try:
            logger.debug("Channel '%s' scheduled" % channel)
            create_notifications_for_channel.apply_async(args=[channel.pk,
                                                               event.pk,
                                                               occurence.pk,
                                                               context])
        except Exception as e:
            log_error_channel(channel, str(e))
            process_exception(e)
            logger.exception(e)
    return occurence


@app.task()
def create_notifications_for_channel(channel_pk, event_pk, occurence_pk, context):
    from bitcaster.models import Channel, Event, Message, Notification

    channel = Channel.objects.get(pk=channel_pk)
    event = Event.objects.get(pk=event_pk)
    logger.debug(f'Processing channel {channel}')
    try:
        message = channel.messages.get(event=event)
        if not message.body.strip():
            msg = _('Empty message for channel %s') % channel
            log_error_event(event, msg)
            raise Exception(msg)
        body_template = Template(message.body)
        subject_template = Template(message.subject)
        organization = channel.organization

    except Message.DoesNotExist as e:
        logger.error(e)
        msg = 'Unable to find a message for %(channel)s'
        log_error_channel(channel, msg)
        raise ObjectDoesNotExist(msg) from e
    except Exception as e:
        process_exception(e)
        raise

    try:
        partition = channel.dispatch_page_size
        page = []
        for subscription in event.subscriptions.valid(channel=channel):
            logger.debug(f'Processing {subscription}')
            ctx = dict(context or {})
            code = subscription.get_code()
            ctx.update({
                'user': subscription.subscriber,
                'subscriber': subscription.subscriber,
                'recipient': subscription.subscriber,
                'event': event,
                'channel': channel,
                'confirmation': absolute_uri(reverse('confirmation', args=[event.pk,
                                                                           subscription.pk,
                                                                           channel.pk,
                                                                           occurence_pk,
                                                                           code])),
                'application': channel.application,
                'organization': organization,
                'subscription': subscription,
                'today': datetime.datetime.today(),
            })
            message = body_template.render(SecureContext(ctx))
            subject = subject_template.render(SecureContext(ctx))
            address = channel.handler.get_recipient_address(subscription)

            notification_kwargs = {'channel': channel,
                                   'event_id': event.pk,
                                   'occurence_id': occurence_pk,
                                   'need_confirmation': event.need_confirmation,
                                   'reminders_timestamps': timezone.now().strftime('%d-%b-%Y %H:%M'),
                                   'max_reminders': event.reminders,
                                   'reminders': 0,
                                   'subscription_id': subscription.pk,
                                   'address': address,
                                   'data': {'subject': subject,
                                            'message': message}
                                   }

            # page.append([address, subject, message, subscription.pk])
            page.append(Notification(**notification_kwargs))

            if len(page) == partition:
                ids = Notification.objects.bulk_create(page)
                log_new_notifications(channel_pk, len(ids))
                page = []

        # process incomplete page
        if len(page):
            ids = Notification.objects.bulk_create(page)
            log_new_notifications(channel_pk, len(ids))

    except Exception as e:
        process_exception(e)
        logger.exception(e)
        raise
    return True


@app.task(bind=True)
def send_page(self, channel_pk: int, occurence_pk: int, page: list):
    from bitcaster.models import Channel, Notification
    channel = Channel.objects.get(pk=channel_pk)
    conn = channel.handler._get_connection()
    for notification_id in page:
        try:
            notification = Notification.objects.pending(occurence=occurence_pk).get(id=notification_id)
        except Notification.DoesNotExist:
            continue
        try:
            channel.handler.emit(notification.address,
                                 notification.data['subject'],
                                 notification.data['message'],
                                 connection=conn)
            log_sent_notification(notification)
        except Exception as e:
            capture_exception(e)
            logger.exception(e)
            log_error_notification(notification, str(e))
    return page
    # resend_failed.apply_async(args=[channel.pk, occurence_pk],
    #                           routing_key='replica',
    #                           queue=fqn(channel.handler),
    #                           countdown=60 + (60 * event.reminder_interval))

    # stats.notification.log(organization, value=len(notifications))
    # counters.notification.log(organization, value=len(notifications))
    # counters.notification.log(channel, value=len(notifications))
    # stats.notification.log(channel, value=len(notifications))
    #
    # counters.notification.log(event, value=len(notifications))
    # stats.notification.log(event, value=len(notifications))


# @app.task()
# def resend_failed(channel_pk, occurence_pk):
#     from bitcaster.models import Notification, Channel, Occurence
#     updates = []
#     ch = Channel.objects.get(pk=channel_pk)
#     occurence = Occurence.objects.get(pk=occurence_pk)
#     event = occurence.event
#
#     handler = ch.handler
#
#     pending = Notification.objects.filter(channel_id=channel_pk,
#                                           occurence=occurence,
#                                           occurence__expire__lt=timezone.now(),
#                                           reminders__lt=F('max_reminders')).exclude(status=Notification.CONFIRMED)
#     for n in pending.all():
#         try:
#             n.reminders += 1
#             n.reminders_timestamps += ', %s' % timezone.now().strftime('%d-%b-%Y %H:%M')
#             message = n.data['message']
#             subject = n.data['subject']
#             if handler.message_class.has_subject:
#                 subject = _('%s - Reminder #%d') % (subject, n.reminders)
#             else:
#                 message += _('%s\n---\nReminder #%d') % (message, n.reminders)
#
#             handler.emit(n.address,
#                          subject,
#                          message)
#             updates.append(n)
#         except Exception:
#             pass
#     Notification.objects.bulk_update(updates, ['reminders', 'reminders_timestamps'])
#     # stats.notification.log(ch.organization, value=len(updates))
#     # stats.notification.log(ch, value=len(updates))
#     # stats.notification.log(event, value=len(updates))
#     if pending.exists():
#         resend_failed.apply_async(args=[channel_pk, occurence_pk],
#                                   routing_key='replica',
#                                   queue=fqn(handler),
#                                   countdown=60 + (60 * event.reminder_interval))


@app.task()
def consolidate_notifications():
    from bitcaster.models import Notification
    Notification.objects.consolidate()
