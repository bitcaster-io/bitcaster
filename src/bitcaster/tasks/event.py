import datetime
from logging import getLogger

from crashlog.middleware import process_exception
from django.core.cache import caches
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.template import Template
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from sentry_sdk import capture_exception

from bitcaster.celery import app
from bitcaster.exceptions import BatchError, LogicError
from bitcaster.template.secure_context import SecureContext
from bitcaster.tsdb.api import (log_error_channel, log_error_event,
                                log_error_notification, log_error_occurence,
                                log_error_retriever, log_new_notifications,
                                log_sent_notification,)
from bitcaster.utils.http import absolute_uri
from bitcaster.utils.reflect import fqn

logger = getLogger(__name__)

cache_lock = caches['lock']


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
                                          event=event):
        if not channel.enabled:
            log_error_channel(channel, _("Channel '%(channel)s' is disabled"))
            logger.error("Channel '%s' is disabled" % channel)
            continue
        if not DispatcherMetaData.objects.is_enabled(handler=fqn(channel.handler)):
            msg = "Channel '%s' is using a disabled dispatcher (%s)" % (channel, channel.handler)
            log_error_channel(channel, _(msg))
            logger.error(msg)
            continue
        try:
            logger.debug("Channel '%s' scheduled" % channel)
            # Chord
            create_notifications_for_channel.apply_async(args=[occurence.pk,
                                                               channel.pk,
                                                               context])
        except Exception as e:
            logger.exception(e)
            log_error_channel(channel, str(e))
            process_exception(e)
    return True


def _get_message_parts(channel, event, header) -> [Template, Template]:
    try:
        message = channel.messages.get(event=event)
        if not message.body.strip():
            msg = _('Empty message for channel %s') % channel
            log_error_event(event, msg)
            raise Exception(msg)
        return Template(message.subject), Template(header + message.body)
    except ObjectDoesNotExist as e:
        msg = 'Unable to find a message for %(channel)s'
        logger.error(e)
        log_error_event(event, msg)
        raise ObjectDoesNotExist(msg) from e
    except Exception as e:
        logger.exception(e)
        process_exception(e)
        raise


@app.task()  # noqa: C901
def create_notifications_for_channel(occurence_pk, channel_pk, context):
    from bitcaster.models import Channel, Notification, Occurence, Address

    channel = Channel.objects.select_related('organization').get(pk=channel_pk)
    organization = channel.organization
    occurence = Occurence.objects.select_related('event').get(pk=occurence_pk)
    event = occurence.event
    application = event.application
    if event.development_mode:
        header = 'DEVELOP MODE ENABLED\n'
        header += application.storage.get('dev_mode_message', application.DEF_MESSAGE)
    else:
        header = ''

    logger.debug(f'Processing channel {channel}')

    subject_template, body_template = _get_message_parts(channel, event, header)

    subscription_filter = {'channel': channel}
    if event.development_mode:
        subscription_filter['subscriber__in'] = event.application.admins
    try:
        partition = 1000
        page = []
        for subscription in event.subscriptions.valid(**subscription_filter):
            try:
                logger.debug(f'Processing {subscription}')
                ctx = dict(context or {})
                code = subscription.get_code()
                ctx.update({
                    'user': subscription.subscriber,
                    'subscriber': subscription.subscriber,
                    'recipient': subscription.subscriber,
                    'event': event,
                    'channel': channel,
                    'development_mode': event.development_mode,
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
                attachments = None
                if event.attachment and channel.handler.handle_attachments:
                    file_getter = event.attachment
                    try:
                        attachment = file_getter.handler.get(subscription)
                        attachments = [attachment]
                    except Exception as e:
                        log_error_retriever(file_getter, str(e))
                        if event.attachment_policy == event.ERROR_IGNORE:
                            attachments = []
                        elif event.attachment_policy == event.ERROR_HALT:
                            continue
                        elif event.attachment_policy == event.ERROR_ABORT:
                            raise BatchError('Error retrieving attachment for %s' % subscription)
                notification_kwargs = {'channel': channel,
                                       'event_id': event.pk,
                                       'occurence_id': occurence_pk,
                                       'need_confirmation': event.need_confirmation,
                                       'reminders_timestamps': timezone.now().strftime('%d-%b-%Y %H:%M'),
                                       'max_reminders': event.reminders,
                                       'development_mode': event.development_mode,
                                       'reminders': 0,
                                       'attachments': attachments,
                                       'subscription_id': subscription.pk,
                                       'address': address,
                                       'next_sent': timezone.now(),
                                       'data': {'subject': subject,
                                                'message': message}
                                       }

                page.append(Notification(**notification_kwargs))

                if len(page) == partition:
                    ids = Notification.objects.bulk_create(page)
                    log_new_notifications(channel_pk, len(ids))
                    page = []
            except Address.DoesNotExist as e:
                logger.exception(e)
                log_error_event(event, 'Address not validated', target=subscription)
                process_exception(e)
            except Exception as e:
                logger.exception(e)
                process_exception(e)
                raise

        # process incomplete page
        if len(page):
            ids = Notification.objects.bulk_create(page)
            log_new_notifications(channel_pk, len(ids))
    except Exception as e:
        logger.exception(e)
        process_exception(e)
        raise
    # from .periodic import process_notifications
    # process_notifications.delay()
    return True


@app.task(bind=True)
def send_page(self, occurence_pk: int, channel_pk: int, page: list):
    if cache_lock.get('STOP'):
        return
    from bitcaster.models import Channel, Notification
    channel = Channel.objects.get(pk=channel_pk)
    handler = channel.handler
    conn = handler._get_connection()
    done = []
    for notification_id in page:
        try:
            notification = Notification.objects.pending(occurence=occurence_pk).get(id=notification_id)
        except Notification.DoesNotExist:
            continue
        subject = notification.data['subject']
        message = notification.data['message']
        if notification.reminders > 0:
            params = dict(subject=subject,
                          message=message,
                          reminder=notification.reminders)
            if handler.message_class.has_subject:
                subject = _('%(subject)s - Reminder #%(reminder)d') % params
            else:
                message += _('%(message)s\n---\nReminder #%(reminder)d') % params

        try:
            channel.handler.emit(notification.address,
                                 subject,
                                 message,
                                 attachments=notification.attachments,
                                 connection=conn)
            log_sent_notification(notification)
            done.append(notification_id)
            if cache_lock.get('STOP'):
                return done
        except Exception as e:
            capture_exception(e)
            logger.exception(e)
            log_error_notification(notification, str(e))
    return done


@app.task()
def consolidate_notifications():
    from bitcaster.models import Notification
    Notification.objects.consolidate()
