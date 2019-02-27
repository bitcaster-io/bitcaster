from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from bitcaster.db.fields import RoleField
from bitcaster.mail import send_mail_by_template
from bitcaster.otp import totp
from bitcaster.utils.http import absolute_uri

from .organization import Organization


class OrganizationMember(models.Model):
    """
    Identifies relationships between teams and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """

    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     db_index=True,
                                     related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             db_index=True,
                             on_delete=models.CASCADE,
                             related_name='memberships')
    # email and team are used only during invitation phase
    # email to check the user invitation, team to automatically
    # enroll the user to selected team
    email = models.EmailField(null=True, blank=True)
    team = models.ForeignKey('bitcaster.Team',
                             blank=True, null=True,
                             on_delete=models.CASCADE)
    role = RoleField()
    date_added = models.DateTimeField(default=timezone.now,
                                      help_text='date when email was sent')
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    date_enrolled = models.DateTimeField(blank=True, null=True,
                                         help_text='date when user first login')

    event = models.ForeignKey('bitcaster.Event',
                              related_name='memberships',
                              default=None, blank=True, null=True,
                              on_delete=models.CASCADE)

    class Meta:
        app_label = 'bitcaster'
        unique_together = (
            ('organization', 'user'),
            ('organization', 'email'),
        )

    # def __str__(self):
    #     return self.user and self.user.email or self.email

    # @transaction.atomic
    def save(self, *args, **kwargs):
        assert self.user_id or self.email, \
            'Must set user or email'
        super(OrganizationMember, self).save(*args, **kwargs)

    # @property
    # def is_pending(self):
    #     return self.user_id is None

    def send_email(self):
        code = totp.now()
        url = reverse('org-member-accept', args=[self.organization.slug, self.pk, code])
        send_mail_by_template('[Bitcaster] invitation',
                              'user_invite', {'membership': self,
                                              'url': absolute_uri(url)},
                              [self.email],
                              async=True)
