from typing import Any

from django.db import models
from django.utils.text import slugify


class SlugMixin(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    slug = models.SlugField(max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(str(self.name))
        super().save(*args, **kwargs)
