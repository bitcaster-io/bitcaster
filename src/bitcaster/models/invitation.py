from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from bitcaster.mail import send_mail_by_template
from bitcaster.otp import totp
from bitcaster.state import get_current_user
from bitcaster.utils.http import absolute_uri

from .application import Application
from .event import Event
from .organization import Organization
from .team import ApplicationRole, Team


class Invitation(models.Model):
    class STATE:
        QUEUED = _('Queued')
        SENT = _('Sent')
        ACCEPTED = _('Accepted')
        CANCELED = _('Canceled')
        EXPIRED = _('Expired')

    target = models.CharField(max_length=200)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True,
                                   on_delete=models.CASCADE,
                                   default=get_current_user,
                                   related_name='invitations')
    organization = models.ForeignKey(Organization,
                                     blank=True, null=True,
                                     on_delete=models.CASCADE,
                                     related_name='invitations')
    application = models.ForeignKey(Application,
                                    blank=True, null=True,
                                    on_delete=models.CASCADE,
                                    related_name='invitations')
    team = models.ForeignKey(Team,
                             blank=True, null=True,
                             on_delete=models.CASCADE,
                             related_name='invitations')
    role = models.ForeignKey(ApplicationRole,
                             blank=True, null=True,
                             on_delete=models.CASCADE,
                             related_name='invitations')
    event = models.ForeignKey(Event,

                              default=None, blank=True, null=True,
                              on_delete=models.CASCADE,
                              related_name='invitations')
    date_created = models.DateTimeField(default=timezone.now,
                                        help_text='date when email was sent')
    date_sent = models.DateTimeField(default=None,
                                     blank=True, null=True,
                                     help_text='date when email was sent')
    date_accepted = models.DateTimeField(blank=True, null=True,
                                         help_text='date when user first login')
    expired = models.BooleanField(default=False)

    class Meta:
        unique_together = (('target', 'application'),
                           ('target', 'organization'),)

    def __str__(self):
        return self.target

    def send_email(self):
        code = totp.now()
        url = reverse('org-member-accept', args=[self.organization.slug, self.pk, code])
        self.date_sent = timezone.now()
        self.save()
        return send_mail_by_template('[Bitcaster] invitation',
                                     'user_invite', {'invitation': self,
                                                     'url': absolute_uri(url)},
                                     [self.target],
                                     async=True)

    def send_sms(self):
        raise NotImplementedError

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.event:
            self.application = self.event.application
            self.organization = self.event.application.organization
        elif self.team:
            self.application = self.team.application
            self.organization = self.application.organization
        elif self.role:
            self.team = self.role.team
            self.application = self.role.team.application
            self.organization = self.role.team.application.organization
        elif self.application:
            self.organization = self.application.organization
        elif self.organization:
            pass
        else:
            raise ValidationError('Cannoo save an Invitation withoune one of event,team,role,application,organization')
        super().save(force_insert, force_update, using, update_fields)
    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):

    # return super().save(commit)
