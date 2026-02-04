import factory

from bitcaster.models import Attachment

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory


class AttachmentFactory(AutoRegisterModelFactory[Attachment]):
    class Meta:
        model = Attachment

    document = factory.django.FileField(from_path="tests/samples/test.txt")
    mime_type = "text/plain"
    correlation_id = factory.Sequence(lambda n: f"correlation-{n}")
    application = factory.SubFactory(ApplicationFactory)
