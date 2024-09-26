# Generated by Django 5.1.1 on 2024-09-26 17:33

import bitcaster.models.key
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bitcaster", "0002_logentry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apikey",
            name="key",
            field=models.CharField(
                default=bitcaster.models.key.make_token, max_length=255, unique=True, verbose_name="Token"
            ),
        ),
        migrations.AlterField(
            model_name="channel",
            name="protocol",
            field=models.CharField(
                choices=[
                    ("PLAINTEXT", "Plaintext"),
                    ("SLACK", "Slack"),
                    ("SMS", "Sms"),
                    ("EMAIL", "Email"),
                    ("WEBPUSH", "Webpush"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="occurrence",
            name="correlation_id",
            field=models.CharField(blank=True, editable=False, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="occurrence",
            name="status",
            field=models.CharField(
                choices=[("NEW", "New"), ("PROCESSED", "Processed"), ("FAILED", "Failed")], default="NEW", max_length=20
            ),
        ),
    ]
