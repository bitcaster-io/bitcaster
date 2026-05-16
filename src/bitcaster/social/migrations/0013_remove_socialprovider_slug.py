from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0012_unique_slug"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="socialprovider",
            name="slug",
        ),
    ]
