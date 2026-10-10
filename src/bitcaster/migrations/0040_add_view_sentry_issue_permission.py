from django.db import migrations


def forwards(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Get or create the content type for bitcaster app
    content_type, created = ContentType.objects.get_or_create(
        app_label="bitcaster",
        model="apikey",
    )

    # Create the permission
    Permission.objects.get_or_create(
        codename="view_sentry_issue",
        name="Can view Sentry issue",
        content_type=content_type,
    )


def backwards(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    Permission.objects.filter(codename="view_sentry_issue").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("bitcaster", "0039_add_view_sentry_issue_grant"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
