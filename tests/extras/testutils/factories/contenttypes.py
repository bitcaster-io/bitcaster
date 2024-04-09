from django.contrib.contenttypes.models import ContentType

from .base import AutoRegisterModelFactory


class ContentTypeFactory(AutoRegisterModelFactory):
    app_label = "auth"
    model = "user"

    class Meta:
        model = ContentType
        django_get_or_create = ("app_label", "model")
