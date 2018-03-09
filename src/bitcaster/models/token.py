import datetime

from django.db import models
from django.utils import timezone

from bitcaster.logging import getLogger
from bitcaster.models.application import Application
from bitcaster.models.base import AbstractModel
from bitcaster.models.user import User
from bitcaster.utils import generate_api_token

logger = getLogger(__name__)

DEFAULT_EXPIRATION = datetime.timedelta(days=30)


def calculate_expiration():
    return timezone.now() + DEFAULT_EXPIRATION


class ApiTriggerKey(AbstractModel):
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    related_name='triggers')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='triggers')
    token = models.CharField(max_length=64, unique=True,
                             default=generate_api_token)
    active = models.BooleanField(default=True, db_index=True)


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
    active = models.BooleanField(default=True, db_index=True)

    @classmethod
    def generate_token(cls):
        return generate_api_token()
