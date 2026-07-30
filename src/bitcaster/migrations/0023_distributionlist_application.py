from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bitcaster", "0022_alter_assignment_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="distributionlist",
            name="application",
            field=models.ForeignKey(
                blank=True,
                help_text="when set, the distribution list is pinned to this application",
                null=True,
                on_delete=models.SET_NULL,
                to="bitcaster.Application",
                verbose_name="Application",
            ),
        ),
    ]
