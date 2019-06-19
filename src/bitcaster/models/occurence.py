import datetime

from django.core.cache import caches
from django.db import models
from django.utils import timezone

from bitcaster.framework.db.fields import EncryptedJSONField
from bitcaster.tasks.model import async

cache_lock = caches['lock']


class OccurenceManager(models.Manager):
    def active(self, *args, **kwargs):
        return Occurence.objects.filter(expire__gt=timezone.now(),
                                        status__in=[Occurence.RUNNING,
                                                    Occurence.READY],
                                        *args, **kwargs)

    def inactive(self):
        return Occurence.objects.filter(expire__lt=timezone.now())

    def consolidate(self):
        for entry in self.filter(organization__isnull=True):
            entry.application = entry.event.application
            entry.organization = entry.application.organization
            entry.save()


class Occurence(models.Model):
    NEW = -2
    READY = -1
    RUNNING = 0
    ABORTED = 1
    EXPIRED = 2
    PAUSED = 3
    TERMINATED = 99
    STATUSES = ((READY, 'Ready'),
                (NEW, 'New'),
                (RUNNING, 'Running'),
                (ABORTED, 'Aborted'),
                (EXPIRED, 'Expired'),
                (PAUSED, 'Paused'),
                (TERMINATED, 'Terminated'),  # all data processed
                )
    ACTIVE = [NEW, READY, RUNNING]
    timestamp = models.DateTimeField(default=timezone.now)
    organization = models.ForeignKey('bitcaster.Organization',
                                     blank=True, null=True,
                                     related_name='occurences',
                                     on_delete=models.CASCADE)
    application = models.ForeignKey('bitcaster.Application',
                                    blank=True, null=True,
                                    related_name='occurences',
                                    on_delete=models.CASCADE)
    event = models.ForeignKey('bitcaster.Event',
                              on_delete=models.CASCADE)
    expire = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(choices=STATUSES,
                                 db_index=True,
                                 default=RUNNING)

    origin = models.GenericIPAddressField(blank=True, null=True)
    token = models.CharField(max_length=64, blank=True, null=True)
    user = models.ForeignKey('bitcaster.User', on_delete=models.CASCADE,
                             blank=True, null=True)
    submissions = models.IntegerField(default=0,
                                      help_text='number of subscriptions')
    successes = models.IntegerField(default=0)
    failures = models.IntegerField(default=0)
    context = EncryptedJSONField(null=True, blank=True)
    # max_loops = models.IntegerField(default=1)
    # loop = models.IntegerField(default=0)

    objects = OccurenceManager()

    processing = models.DateTimeField(blank=True,
                                      null=True)

    class Meta:
        app_label = 'bitcaster'

    def __str__(self):
        return '#{} {}'.format(self.pk, self.timestamp.strftime('%d %b %Y'), self.event)

    @async(queue='consolidate')
    def consolidate(self):
        self.application = self.event.application
        self.organization = self.application.organization
        self.save()
        return self

    @classmethod
    def log(cls, event, **kwargs):
        now = timezone.now()
        expire = now + datetime.timedelta(seconds=event.event_expiration)
        obj = cls.objects.create(event=event,
                                 timestamp=now,
                                 expire=expire,
                                 **kwargs)
        obj.consolidate()
        return obj

    def ttl(self):
        return

    def start(self):
        self.status = Occurence.RUNNING
        self.save()

    def terminate(self):
        if self.status in Occurence.ACTIVE:
            self.status = Occurence.TERMINATED
            self.save()

    def lock(self):
        if self.processing is None:
            ret = Occurence.objects.filter(pk=self.pk,
                                           processing__isnull=True).update(
                processing=timezone.now())
            return len(ret) == 1
        return False

    def locked(self):
        return self.processing

    def unlock(self):
        ret = Occurence.objects.filter(pk=self.pk,
                                       processing__isnull=False).update(processing=None)
        return len(ret) == 1
