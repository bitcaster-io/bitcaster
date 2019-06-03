from django.db import models

from .base import AbstractModel
from .event import Event
from .user import User


class ControlCode(AbstractModel):
    event = models.ForeignKey(Event,
                              on_delete=models.CASCADE)
    subscriber = models.ForeignKey(User,
                                   on_delete=models.CASCADE)
    code = models.CharField(max_length=5)


class Aknowledge(AbstractModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
