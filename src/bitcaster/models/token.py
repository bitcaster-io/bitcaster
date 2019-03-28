import datetime
from logging import getLogger

from django.db import models

from bitcaster.models import Event
from bitcaster.models.application import Application
from bitcaster.models.base import AbstractModel
from bitcaster.models.mixins import ReverseWrapperMixin
from bitcaster.models.user import User
from bitcaster.utils.tokens import generate_api_token

logger = getLogger(__name__)

DEFAULT_EXPIRATION = datetime.timedelta(days=30)


# def calculate_expiration():
#     return timezone.now() + DEFAULT_EXPIRATION
#

class ApplicationTriggerKey(ReverseWrapperMixin, AbstractModel):
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    related_name='keys')
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=64, unique=True,
                             default=generate_api_token)
    enabled = models.BooleanField(default=True, db_index=True)

    events = models.ManyToManyField(Event, related_name='keys')
    all_events = models.BooleanField(default=False)

    class Meta:
        app_label = 'bitcaster'
        verbose_name = 'Key'
        verbose_name_plural = 'Keys'

    class Reverse:
        pattern = 'app-key-{op}'
        args = ['application.organization.slug', 'application.slug', 'id']

    def __str__(self):
        return self.name


class ApiAuthToken(AbstractModel):
    # users can generate tokens without being application-bound
    application = models.ForeignKey(Application,
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE,
                                    related_name='tokens')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='tokens')

    token = models.CharField(max_length=64, unique=True,
                             default=generate_api_token)
    enabled = models.BooleanField(default=True, db_index=True)

    class Meta:
        app_label = 'bitcaster'

    # @classmethod
    # def generate_token(cls):
    #     return generate_api_token()
#
