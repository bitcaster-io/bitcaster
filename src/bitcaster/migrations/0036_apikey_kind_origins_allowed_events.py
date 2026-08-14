# Generated manually

from django.contrib.postgres.fields import ArrayField
from django.db import migrations, models

import bitcaster.models.key


class Migration(migrations.Migration):
    dependencies = [
        ("bitcaster", "0035_applicationmembership_active_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="apikey",
            name="kind",
            field=models.CharField(
                choices=[("SERVER", "Server"), ("PUBLIC", "Public")],
                default=bitcaster.models.key.KeyKind["SERVER"],
                help_text="PUBLIC keys are bound to declared origins and restricted to event triggering.",
                max_length=16,
                verbose_name="Kind",
            ),
        ),
        migrations.AddField(
            model_name="apikey",
            name="origins",
            field=ArrayField(
                base_field=models.CharField(blank=True, max_length=255, null=True),
                blank=True,
                help_text="Allowed origins for PUBLIC keys. Requests with other origins are rejected.",
                null=True,
                size=None,
                verbose_name="Origins",
            ),
        ),
        migrations.AddField(
            model_name="apikey",
            name="allowed_events",
            field=ArrayField(
                base_field=models.CharField(blank=True, max_length=64, null=True),
                blank=True,
                help_text="Optional event slug allowlist for PUBLIC keys. Empty means any event of the application.",
                null=True,
                size=None,
                verbose_name="Allowed events",
            ),
        ),
    ]
