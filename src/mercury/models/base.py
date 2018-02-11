# -*- coding: utf-8 -*-
from django.db import models

from concurrency.fields import IntegerVersionField

from mercury import logging

logger = logging.getLogger(__name__)


class AbstractModel(models.Model):
    version = IntegerVersionField()
    last_modify_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
