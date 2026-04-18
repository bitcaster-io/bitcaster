from django.db import models
from django.utils.translation import gettext as _


class User(models.Model):
    # ok: django-fields-required-attrs
    first_name = models.CharField(
        max_length=30,
        verbose_name=_("First Name"),
        help_text=_("First Name"),
    )

    # ruleid: django-fields-required-attrs
    last_name = models.CharField(
        max_length=30,
        help_text=_("last Name"),
        unique=True,
    )

    # ruleid: django-fields-required-attrs
    full_name = models.CharField(
        max_length=30,
        verbose_name=_("Full Name"),
        unique=True,
    )
