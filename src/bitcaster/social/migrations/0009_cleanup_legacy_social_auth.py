from django.db import migrations


def drop_legacy_tables(apps, schema_editor):
    tables = [
        "social_auth_usersocialauth",
        "social_auth_nonce",
        "social_auth_association",
        "social_auth_code",
        "social_auth_partial",
    ]
    with schema_editor.connection.cursor() as cursor:
        # We check for existence to avoid errors on fresh installs
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0008_alter_socialprovider_provider"),
    ]

    operations = [
        migrations.RunPython(drop_legacy_tables, migrations.RunPython.noop),
    ]
