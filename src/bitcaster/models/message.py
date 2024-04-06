import logging
from typing import Any, Dict

from django.db import models
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class Message(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    content = models.TextField(_("Content"))
    channel = models.ForeignKey("Channel", on_delete=models.CASCADE, related_name="channels")
    event = models.ForeignKey("EventType", on_delete=models.CASCADE, related_name="messages")

    subject = models.TextField(_("subject"), blank=True, null=True)

    class Meta:
        verbose_name = _("Message template")
        verbose_name_plural = _("Message templates")

    def __str__(self) -> str:
        return self.name

    def render(self, context: Dict[str, Any]) -> str:
        tpl = Template(self.content)
        return tpl.render(Context(context))
