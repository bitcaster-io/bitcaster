import os
from typing import Any

import sentry_sdk
from celery import Celery, signals
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcaster.config.settings")
app = Celery("hcr")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name="tasks")


@signals.celeryd_init.connect
def init_sentry(**_kwargs: Any) -> None:
    sentry_sdk.set_tag("celery", True)
