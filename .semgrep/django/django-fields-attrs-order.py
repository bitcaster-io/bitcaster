from django.db import models
from django.utils.translation import gettext as _


class TestModel(models.Model):
    # OK: Correct order
    # ok: django-field-attribute-order
    name = models.CharField(verbose_name="Name", max_length=100, blank=True, help_text="Enter full name")

    # ok: django-field-attribute-order
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
        related_name="tests",
        blank=True,
        null=True,
        default=None,
        db_index=True,
        help_text="The user",
    )

    # ok: django-field-attribute-order
    date = models.DateTimeField(
        verbose_name="Created",
        null=True,
        default=None,
        editable=False,
        auto_now_add=True,
    )

    # ok: django-field-attribute-order
    complex_field = models.CharField(
        verbose_name="Complex",
        max_length=10,
        choices=[(1, 1)],
        blank=True,
        null=True,
        default="",
        db_index=True,
        db_collation="utf8",
        unique=True,
        editable=True,
        validators=[],
        help_text="Complex",
    )

    # ok: django-field-attribute-order
    others_ok = models.IntegerField(
        verbose_name="Other",
        other_arg="Other",
        validators=[],
        help_text="Help",
    )

    # ok: django-field-attribute-order
    array_field = ChoiceArrayField(
        base_field=models.CharField(max_length=32),
        verbose_name="Array",
    )

    # ruleid: django-field-attribute-order
    bad_1 = models.CharField(
        max_length=100,
        verbose_name="Name",
    )

    # ruleid: django-field-attribute-order
    bad_2 = models.IntegerField(
        null=True,
        blank=True,
    )

    # ruleid: django-field-attribute-order
    bad_3 = models.ForeignKey(
        "auth.User",
        related_name="tests",
        on_delete=models.CASCADE,
    )

    # ruleid: django-field-attribute-order
    bad_4 = models.IntegerField(
        db_index=True,
        null=True,
    )

    # ruleid: django-field-attribute-order
    bad_5 = models.IntegerField(
        unique=True,
        db_collation="utf8",
    )

    # ruleid: django-field-attribute-order
    bad_6 = models.DateTimeField(
        auto_now_add=True,
        auto_now=True,
    )

    # ruleid: django-field-attribute-order
    bad_7 = models.CharField(
        chained_model_field="slug",
        chained_field="parent",
    )

    # ruleid: django-field-attribute-order
    bad_8 = models.IntegerField(
        help_text="Help",
        validators=[],
    )

    # ruleid: django-field-attribute-order
    bad_9 = models.IntegerField(
        validators=[],
        editable=True,
    )

    # ruleid: django-field-attribute-order
    bad_10 = models.CharField(
        other_arg="Other",
        unique=True,
    )

    # ruleid: django-field-attribute-order
    bad_11 = models.IntegerField(
        default=0,
        null=True,
    )
