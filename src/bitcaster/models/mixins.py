from typing import TYPE_CHECKING, Any, Iterable, Mapping

from concurrency.fields import IntegerVersionField
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.base import ModelBase
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel_co

    from .application import Application
    from .organization import Organization


class LockMixin(models.Model):
    locked = models.BooleanField(
        verbose_name=_("locked"), default=False, help_text=_("If checked any notification is ignored and not forwarded")
    )
    paused = models.BooleanField(
        verbose_name=_("paused"), default=False, help_text=_("If checked any notification paused")
    )

    class Meta:
        abstract = True

    def can_be_locked(self) -> bool:
        raise NotImplementedError

    def lock(self) -> None:
        if not self.locked:
            self.locked = True
            self.save()

    def unlock(self) -> None:
        if self.locked:
            self.locked = False
            self.save()

    def pause(self) -> None:
        if not self.paused:
            self.paused = True
            self.save()

    def resume(self) -> None:
        if self.paused:
            self.paused = False
            self.save()


class AdminReversable(models.Model):
    class Meta:
        abstract = True

    def get_admin_change(self) -> str:
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.pk,))


class BaseQuerySet(models.QuerySet["AnyModel_co"]):
    def get(self, *args: Any, **kwargs: Any) -> "AnyModel_co":
        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist as e:
            raise self.model.DoesNotExist(
                "%s matching query does not exist. Using %s %s" % (self.model._meta.object_name, args, kwargs)
            ) from e


class BitcasterBaselManager(models.Manager["AnyModel_co"]):
    _queryset_class = BaseQuerySet


class BitcasterBaseModel(AdminReversable):
    version = IntegerVersionField()
    last_updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

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


class ScopedManager(BitcasterBaselManager["AnyModel_co"]):
    def get_or_create(self, defaults: Mapping[str, Any] | None = None, **kwargs: Any) -> "tuple[AnyModel_co, bool]":
        values = dict(**(defaults or {}))
        if kwargs.get("application"):
            kwargs["project"] = kwargs["application"].project

        if kwargs.get("project"):
            kwargs["organization"] = kwargs["project"].organization

        if values:
            if values.get("application"):
                values["project"] = values["application"].project

            if values.get("project"):
                values["organization"] = values["project"].organization

        return super().get_or_create(values, **kwargs)

    def update_or_create(
        self,
        defaults: Mapping[str, Any] | None = None,
        create_defaults: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> "tuple[AnyModel_co, bool]":
        values = dict(**(defaults or {}))
        if kwargs.get("application"):
            kwargs["project"] = kwargs["application"].project

        if kwargs.get("project"):
            kwargs["organization"] = kwargs["project"].organization

        if values:
            if values.get("application"):
                values["project"] = values["application"].project

            if values.get("project"):
                values["organization"] = values["project"].organization
        return super().update_or_create(values, **kwargs)


class Scoped2Mixin(models.Model):
    organization: "Organization"
    organization = models.ForeignKey("Organization", related_name="%(class)s_set", on_delete=models.CASCADE, blank=True)
    project = ChainedForeignKey(
        "Project",
        blank=True,
        null=True,
        chained_field="organization",
        chained_model_field="organization",
        show_all=False,
        related_name="%(class)s_set",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Scoped3Mixin(Scoped2Mixin):
    application: "Application"
    application = ChainedForeignKey(
        "Application",
        blank=True,
        null=True,
        chained_field="project",
        chained_model_field="project",
        show_all=False,
        related_name="%(class)s_set",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
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
