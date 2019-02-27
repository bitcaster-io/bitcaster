from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from bitcaster.models import ApplicationTriggerKey, Channel, Event, Message
from bitcaster.models.configurationissue import (check_application,
                                                 check_organization,)


@receiver([post_save, post_delete], sender=Channel, dispatch_uid='channel-check-config')
@receiver([post_save, post_delete], sender=Event, dispatch_uid='event-check-config')
@receiver([post_save, post_delete], sender=Message, dispatch_uid='message-check-config')
@receiver([post_save, post_delete], sender=ApplicationTriggerKey, dispatch_uid='app-check-config')
def check_config(sender, instance, **kwargs):
    if getattr(instance, 'application', None):
        check_application(instance.application)
    elif getattr(instance, 'organization', None):
        check_organization(instance.organization)

#
# @receiver([post_save, post_delete], sender=Organization)
# def check_config(sender, instance, **kwargs):
#     pass
#
#
# @receiver([post_save, post_delete], sender=Application)
# def check_config(sender, instance, **kwargs):
#     pass
