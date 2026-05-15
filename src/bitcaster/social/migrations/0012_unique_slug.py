from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0011_add_slug_to_socialprovider"),
    ]

    operations = [
        migrations.AlterField(
            model_name="socialprovider",
            name="slug",
            field=models.SlugField(
                help_text="Unique identifier used in login URLs",
                max_length=50,
                unique=True,
                verbose_name="Slug",
            ),
        ),
    ]
