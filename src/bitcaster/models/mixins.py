from typing import TYPE_CHECKING, Any, Iterable, MutableMapping, Optional

from concurrency.fields import IntegerVersionField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.utils.text import slugify
from django.utils.translation import gettext as _

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel

    from .application import Application
    from .organization import Organization


class LockMixin(models.Model):
    locked = models.BooleanField(default=False, help_text=_("Security lock of project"))

    class Meta:
        abstract = True


class BaseQuerySet(models.QuerySet["AnyModel"]):

    def get(self, *args: Any, **kwargs: Any) -> "AnyModel":
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist(
                "%s matching query does not exist. Using %s %s" % (self.model._meta.object_name, args, kwargs)
            )


class BitcasterBaselManager(models.Manager["AnyModel"]):
    _queryset_class = BaseQuerySet


class BitcasterBaseModel(models.Model):
    version = IntegerVersionField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def natural_key(self) -> tuple[str | None, ...]:
        raise NotImplementedError


class SlugMixin(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return str(self.name)

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(str(self.name))
        super().save(*args, **kwargs)


class ScopedManager(BitcasterBaselManager["AnyModel"]):

    def get_or_create(self, defaults: MutableMapping[str, Any] | None = None, **kwargs: Any) -> "tuple[AnyModel, bool]":
        if kwargs.get("application", None):
            kwargs["project"] = kwargs["application"].project

        if kwargs.get("project", None):
            kwargs["organization"] = kwargs["project"].organization

        if defaults:
            if defaults.get("application", None):
                defaults["project"] = defaults["application"].project

            if defaults.get("project", None):
                defaults["organization"] = defaults["project"].organization

        return super().get_or_create(defaults, **kwargs)

    def update_or_create(
        self,
        defaults: MutableMapping[str, Any] | None = None,
        create_defaults: MutableMapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> "tuple[AnyModel, bool]":
        if kwargs.get("application", None):
            kwargs["project"] = kwargs["application"].project

        if kwargs.get("project", None):
            kwargs["organization"] = kwargs["project"].organization

        if defaults:
            if defaults.get("application", None):
                defaults["project"] = defaults["application"].project

            if defaults.get("project", None):
                defaults["organization"] = defaults["project"].organization
        return super().update_or_create(defaults, **kwargs)


class Scoped2Mixin(models.Model):
    organization: "Organization"
    organization = models.ForeignKey("Organization", related_name="%(class)s_set", on_delete=models.CASCADE, blank=True)
    project = models.ForeignKey(
        "Project", related_name="%(class)s_set", on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        abstract = True


class Scoped3Mixin(Scoped2Mixin):
    application: "Application"
    application = models.ForeignKey(
        "Application", related_name="%(class)s_set", on_delete=models.CASCADE, blank=True, null=True
    )

    class Meta:
        abstract = True

    def clean(self) -> None:
        try:
            if self.application:
                self.project = self.application.project
        except ObjectDoesNotExist:  # pragma: no cover
            pass
        try:
            if self.project:
                self.organization = self.project.organization
        except ObjectDoesNotExist:  # pragma: no cover
            pass
        super().clean()

    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        try:
            if self.application:
                self.project = self.application.project
        except ObjectDoesNotExist:  # pragma: no cover
            pass
        try:
            if self.project:
                self.organization = self.project.organization
        except ObjectDoesNotExist:  # pragma: no cover
            pass
        super().save(force_insert, force_update, using, update_fields)
