# Generated by Django 5.1.1 on 2024-09-20 19:30

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("bitcaster", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Browser",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("bitcaster.assignment",),
        ),
    ]
