from django.conf import settings
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from mercury.db.fields import RoleField
from mercury.mail import send_mail_by_template
from mercury.otp import totp
from mercury.utils.http import absolute_uri

from .organization import Organization


class OrganizationMember(models.Model):
    """
    Identifies relationships between teams and users.

    Users listed as team members are considered to have access to all projects
    and could be thought of as team owners (though their access level may not)
    be set to ownership.
    """
    __core__ = True

    organization = models.ForeignKey(Organization,
                                     on_delete=models.CASCADE,
                                     related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             on_delete=models.CASCADE,
                             related_name='memberships')
    email = models.EmailField(null=True, blank=True)

    role = RoleField()
    date_added = models.DateTimeField(default=timezone.now)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   null=True, blank=True,
                                   on_delete=models.CASCADE,
                                   related_name='+')
    date_enrolled = models.DateTimeField(blank=True,
                                         null=True)

    class Meta:
        unique_together = (
            ('organization', 'user'),
            ('organization', 'email'),
        )

    def __str__(self):
        return f"{self.organization} {self.user}/{self.role}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        assert self.user_id or self.email, \
            'Must set user or email'
        super(OrganizationMember, self).save(*args, **kwargs)

    @property
    def is_pending(self):
        return self.user_id is None

    def send_email(self):
        code = totp.now()
        url = reverse('invitation-accept', args=[self.organization.slug, self.pk, code])
        send_mail_by_template('[Bitcaster] invitation',
                              'user_invite', {'email': self.email,
                                              'url': absolute_uri(url)},
                              [self.email],
                              async=True)
