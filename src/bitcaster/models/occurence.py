from django.db import models


class Occurence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey('bitcaster.Organization',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
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
