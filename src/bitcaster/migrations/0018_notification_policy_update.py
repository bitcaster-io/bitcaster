from typing import Any

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def update_notification_policy(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Notification: type[Any] = apps.get_model("bitcaster", "Notification")

    # Notification.policy = 4 if Notification.dynamic
    Notification.objects.filter(dynamic=True).update(policy=4)

    # Notification.policy = 3 if Notification.external_filtering
    # We should decide which takes precedence if both are True.
    # Following user's order, external_filtering updates after dynamic.
    Notification.objects.filter(external_filtering=True).update(policy=3)


def reverse_update_notification_policy(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Notification: type[Any] = apps.get_model("bitcaster", "Notification")
    Notification.objects.all().update(policy=1)  # Reset to FILTERING_ALWAYS


class Migration(migrations.Migration):
    dependencies = [
        ("bitcaster", "0017_notification_context_filter_notification_description_and_more"),
    ]

    operations = [
        migrations.RunPython(update_notification_policy, reverse_update_notification_policy),
    ]
