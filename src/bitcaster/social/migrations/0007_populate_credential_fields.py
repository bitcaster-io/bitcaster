from django.db import migrations


def populate_fields(apps, schema_editor):
    SocialProvider = apps.get_model("social", "SocialProvider")

    for obj in SocialProvider.objects.all():
        conf = obj.configuration

        # New format
        client_id = conf.get("client_id")
        secret = conf.get("secret")
        key = conf.get("key")

        # Populate new columns
        if client_id:
            obj.client_id = client_id
        if secret:
            obj.secret = secret
        if key:
            obj.key = key

        # Clean JSON if data was moved
        new_conf = {k: v for k, v in conf.items() if k not in ["client_id", "secret", "key"]}
        obj.configuration = new_conf
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0006_add_credential_fields"),
    ]

    operations = [
        migrations.RunPython(populate_fields, migrations.RunPython.noop),
    ]
