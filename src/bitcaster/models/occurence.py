from django.db import models
from django.utils import timezone

from bitcaster.state import state
# from .event import Event
from bitcaster.utils.wsgi import get_client_ip


class Occurence(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    organization = models.ForeignKey('bitcaster.Organization',
                                     related_name='occurences',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    related_name='occurences',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('bitcaster.Event',
                              on_delete=models.CASCADE)
    origin = models.GenericIPAddressField(blank=True, null=True)
    token = models.CharField(max_length=64, blank=True, null=True)
    user = models.ForeignKey('bitcaster.User', on_delete=models.CASCADE,
                             blank=True, null=True)
    submissions = models.IntegerField(default=0,
                                      help_text='number of subscriptions')
    successes = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)

    class Meta:
        app_label = 'bitcaster'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.application = self.event.application
        self.organization = self.application.organization
        super().save(force_insert, force_update, using, update_fields)

    @classmethod
    def log(self, event, **kwargs):
        request = kwargs.pop('request', state.request)
        kwargs.setdefault('application', event.application)
        kwargs.setdefault('organization', event.application.organization)
        kwargs.setdefault('origin', get_client_ip(request))

        obj = Occurence(event=event, **kwargs)
        obj.save()
        return obj
