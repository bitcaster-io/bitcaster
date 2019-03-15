from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from bitcaster.mail import send_mail_by_template
from bitcaster.otp import totp
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

    def send_email(self):
        code = totp.now()
        url = reverse('org-member-accept', args=[self.organization.slug, self.pk, code])
        send_mail_by_template('[Bitcaster] invitation',
                              'user_invite', {'membership': self,
                                              'url': absolute_uri(url)},
                              [self.target],
                              async=True)

    def send_sms(self):
        raise NotImplementedError
