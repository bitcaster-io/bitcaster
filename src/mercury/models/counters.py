# -*- coding: utf-8 -*-
from django.db import models


class CounterMixin(models.Model):
    totals = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)

    class Meta:
        abstract = True
