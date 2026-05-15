from django.db import migrations, models


def populate_slug(apps, schema_editor):
    SocialProvider = apps.get_model("social", "SocialProvider")
    for obj in SocialProvider.objects.all():
        if obj.provider == "openid_connect":
            obj.slug = f"openid_connect-{obj.pk}"
        else:
            obj.slug = obj.provider
        obj.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0010_alter_socialprovider_provider_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="socialprovider",
            name="slug",
            field=models.SlugField(
                blank=True,
                help_text="Unique identifier used in login URLs",
                null=True,
                verbose_name="Slug",
            ),
        ),
        migrations.RunPython(populate_slug, migrations.RunPython.noop),
    ]
