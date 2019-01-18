from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from bitcaster.models import ApplicationTriggerKey, Channel, Event, Message
from bitcaster.models.configurationissue import (check_application,
                                                 check_organization,)


@receiver([post_save, post_delete], sender=Channel)
@receiver([post_save, post_delete], sender=Event)
@receiver([post_save, post_delete], sender=Message)
@receiver([post_save, post_delete], sender=ApplicationTriggerKey)
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
