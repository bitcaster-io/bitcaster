from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.text import slugify


class SlugMixin(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    slug = models.SlugField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(str(self.name))
        super().save(*args, **kwargs)


class ScopedMixin(models.Model):

    organization = models.ForeignKey("Organization", on_delete=models.CASCADE, blank=True)
    project = models.ForeignKey("Project", on_delete=models.CASCADE, blank=True, null=True)
    application = models.ForeignKey("Application", on_delete=models.CASCADE, blank=True, null=True)

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
