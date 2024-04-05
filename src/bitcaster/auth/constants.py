from django.db.models import TextChoices


class Grant(TextChoices):
    EVENT_TRIGGER = "TRIGGER", "Trigger"
