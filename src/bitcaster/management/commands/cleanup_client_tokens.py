from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from bitcaster.models import ClientToken


class Command(BaseCommand):
    help = "Delete expired client tokens"

    def handle(self, *args: Any, **options: Any) -> None:
        deleted, _ = ClientToken.objects.filter(expires_at__lte=timezone.now()).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} expired client tokens"))
