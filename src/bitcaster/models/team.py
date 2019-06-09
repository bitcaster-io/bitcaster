from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from bitcaster.models.mixins import ReverseWrapperMixin

from .application import Application
from .applicationuser import ApplicationUser
from .base import AbstractModel
from .user import User


class ApplicationTeam(ReverseWrapperMixin, AbstractModel):
    name = models.CharField(max_length=100)
    application = models.ForeignKey(Application,
                                    related_name='teams',
                                    on_delete=models.CASCADE)
    memberships = models.ManyToManyField(ApplicationUser)

    class Meta:
        app_label = 'bitcaster'
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')

    class Reverse:
        pattern = 'app-team-{op}'
        args = ['application.organization.slug', 'application.slug', 'id']

    def __str__(self):
        return self.name

    @cached_property
    def members(self):
        return User.objects.filter(memberships__applications__application__teams=self)
