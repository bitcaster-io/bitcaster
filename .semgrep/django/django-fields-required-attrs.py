from django.db import models
from django.utils.translation import gettext as _


class User(models.Model):
    # ok: django-field-verbose-name-required
    # ok: django-field-help-text-required
    # ok: django-field-verbose-name-gettext
    # ok: django-field-help-text-gettext
    first_name = models.CharField(
        max_length=30,
        verbose_name=_("First Name"),
        help_text=_("First Name"),
    )

    # ruleid: django-field-verbose-name-required
    # ok: django-field-help-text-required
    last_name = models.CharField(
        max_length=30,
        help_text=_("last Name"),
        unique=True,
    )

    # ruleid: django-field-help-text-required
    # ok: django-field-verbose-name-required
    full_name = models.CharField(
        max_length=30,
        verbose_name=_("Full Name"),
        unique=True,
    )

    # ruleid: django-field-verbose-name-gettext
    # ok: django-field-help-text-gettext
    email = models.EmailField(
        verbose_name="Email Address",
        help_text=_("User email address"),
    )

    # ruleid: django-field-help-text-gettext
    # ok: django-field-verbose-name-gettext
    address = models.CharField(
        verbose_name=_("Address"),
        help_text="User home address",
    )

    # ruleid: django-field-help-text-gettext
    address = models.CharField(
        verbose_name="Address",
        help_text="User home address",
    )
