import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import strategy_field.fields
from django.conf import settings
from django.contrib.postgres.operations import CreateCollation
from django.db import migrations, models

import bitcaster.models.auth

# Generated by Django 5.0.3 on 2024-04-09 21:34


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        CreateCollation("case_insensitive", provider="icu", locale="und-u-ks-level2", deterministic=False),
        migrations.CreateModel(
            name="Application",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255, unique=True)),
                ("active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255)),
                ("value", models.CharField(max_length=255)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="addresses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "name"), ("user", "value")},
            },
        ),
        migrations.CreateModel(
            name="ApiKey",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255)),
                ("token", models.CharField(default=bitcaster.models.auth.make_token, unique=True)),
                (
                    "grants",
                    bitcaster.models.auth.ChoiceArrayField(
                        base_field=models.CharField(max_length=255),
                        blank=True,
                        choices=[
                            ("USER_READ", "User Read"),
                            ("USER_WRITE", "User Write"),
                            ("USER_ADMIN", "User Admin"),
                            ("ORG_READ", "Organization Read"),
                            ("ORG_WRITE", "Organization Write"),
                            ("ORG_ADMIN", "Organization Admin"),
                            ("PROJECT_READ", "Project Read"),
                            ("PROJECT_WRITE", "Project Write"),
                            ("PROJECT_ADMIN", "Project Admin"),
                            ("PROJECT_LOCKOUT", "Project Lockout"),
                            ("APP_READ", "Application Read"),
                            ("APP_WRITE", "Application Write"),
                            ("APP_ADMIN", "Application Admin"),
                            ("APP_LOCKOUT", "Application Lockout"),
                            ("EVENT_ADMIN", "Event Admin"),
                            ("EVENT_READ", "Event Read"),
                            ("EVENT_WRITE", "Event Write"),
                            ("EVENT_TRIGGER", "Event Trigger"),
                            ("EVENT_LOCKOUT", "Event Lockout"),
                            ("MESSAGE_READ", "Message Read"),
                            ("MESSAGE_WRITE", "Message Write"),
                            ("MESSAGE_ADMIN", "Message Admin"),
                            ("CHANNEL_READ", "Channel Read"),
                            ("CHANNEL_WRITE", "Channel Write"),
                            ("CHANNEL_ADMIN", "Channel Admin"),
                            ("CHANNEL_LOCKOUT", "Channel Lockout"),
                        ],
                        null=True,
                        size=None,
                    ),
                ),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                (
                    "application",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.application"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Channel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255)),
                ("dispatcher", strategy_field.fields.StrategyField(default="test")),
                ("config", models.JSONField(blank=True, default=dict)),
                ("active", models.BooleanField(default=True)),
                ("locked", models.BooleanField(default=False)),
                (
                    "application",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="bitcaster.application"
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="bitcaster.organization"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255)),
                ("description", models.CharField(max_length=255)),
                ("active", models.BooleanField(default=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_types",
                        to="bitcaster.application",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LogEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "level",
                    models.CharField(
                        choices=[
                            ("CRITICAL", "CRITICAL"),
                            ("FATAL", "FATAL"),
                            ("ERROR", "ERROR"),
                            ("WARN", "WARN"),
                            ("WARNING", "WARNING"),
                            ("INFO", "INFO"),
                            ("DEBUG", "DEBUG"),
                            ("NOTSET", "NOTSET"),
                        ],
                        max_length=255,
                    ),
                ),
                ("message", models.TextField()),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "application",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.application"),
                ),
            ],
            options={
                "verbose_name": "Log Entry",
                "verbose_name_plural": "Log Entries",
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                ("subject", models.TextField(blank=True, null=True, verbose_name="subject")),
                ("content", models.TextField(verbose_name="Content")),
                ("html_content", models.TextField(verbose_name="HTML Content")),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="channels", to="bitcaster.channel"
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="bitcaster.event"
                    ),
                ),
            ],
            options={
                "verbose_name": "Message template",
                "verbose_name_plural": "Message templates",
            },
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_collation="case_insensitive", max_length=255, unique=True)),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.organization"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="application",
            name="project",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.project"),
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth.group")),
                (
                    "organization",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="bitcaster.organization"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="roles", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payload_filter", models.TextField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
                ("channels", models.ManyToManyField(related_name="subscriptions", to="bitcaster.channel")),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="subscriptions", to="bitcaster.event"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Subscription",
                "verbose_name_plural": "Subscriptions",
            },
        ),
        migrations.CreateModel(
            name="Validation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("validated", models.BooleanField(default=False)),
                (
                    "address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="validations", to="bitcaster.address"
                    ),
                ),
                (
                    "channel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="validations", to="bitcaster.channel"
                    ),
                ),
            ],
            options={
                "unique_together": {("address", "channel")},
            },
        ),
    ]
