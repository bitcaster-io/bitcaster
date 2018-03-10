import os
import sys

import environ
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.core.management.base import BaseCommand
from strategy_field.utils import fqn, import_by_name

from bitcaster.db.fields import Role
from bitcaster.models import (Application, Channel,
                              Organization, Subscription, User,)

TEMPLATE_ENV = b"""
ADMIN_EMAIL=
DEBUG=True
DATABASE_URL=psql://postgres:@127.0.0.1:5432/bitcaster
SECRET_KEY=

EMAIL_HOST=
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=
EMAIL_USE_TLS=

CACHE_URL=rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient
CELERY_BROKER_URL=redis://127.0.0.1:6379/0

ENABLE_SENTRY=0
SENTRY_DSN=

SLACK_APP_ID=
SLACK_APP_SECRET=
SLACK_APP_TOKEN=

GOOGLE_APP_ID=
GOOGLE_APP_SECRET=

TWITTER_APP_KEY=
TWITTER_APP_SECRET=

RECAPTCHA_PUBLIC_KEY=
RECAPTCHA_PRIVATE_KEY=

"""

TEMPLATE_DEMO = b"""
ADMIN_EMAIL=
DEBUG=True
DATABASE_URL=psql://postgres:@127.0.0.1:5432/bitcaster
SECRET_KEY=123

USER1_NAME=
USER1_FRIENDLY_NAME=
USER1_EMAIL=
USER1_WHATSAPP=
USER1_TWILIO=
USER1_SLACK=
USER1_IRC_RECIPIENT=
USER1_XMPP_RECIPIENT=
USER1_SKYPE_RECIPIENT=

USER2_NAME=
USER2_FRIENDLY_NAME=
USER2_EMAIL=
USER2_WHATSAPP=
USER2_TWILIO=
USER2_SLACK=

# CHANNELS=gmail,twilio,slack,plivio,irc,xmpp,skype,hangout

; create password at https://myaccount.google.com/apppasswords
CHANNEL_GMAIL_USERNAME=
CHANNEL_GMAIL_PASSWORD=
CHANNEL_GMAIL_SENDER=bitcaster@noreply.org

; use yowsup-cli to register
; see: https://github.com/tgalal/yowsup/wiki/yowsup-cli-2.0#yowsup-cli-registration
CHANNEL_WHATSAPP_LOGIN=
CHANNEL_WHATSAPP_PASSWORD=

; get your token at https://www.twilio.com/console
CHANNEL_TWILIO_SID=
CHANNEL_TWILIO_TOKEN=
;get twilio number  at https://www.twilio.com/console/phone-numbers/incoming
CHANNEL_TWILIO_SENDER=

; get legacy token at https://api.slack.com/custom-integrations/legacy-tokens
CHANNEL_SLACK_TOKEN=

CHANNEL_PLIVO_SID=
CHANNEL_PLIVO_TOKEN=
CHANNEL_PLIVO_SENDER=

CHANNEL_IRC_USERNAME=
CHANNEL_IRC_PASSWORD=

CHANNEL_XMPP_USERNAME=
CHANNEL_XMPP_PASSWORD=

CHANNEL_SKYPE_USERNAME=
CHANNEL_SKYPE_PASSWORD=

CHANNEL_FACEBOOK_KEY=
CHANNEL_FACEBOOK_PASSWORD=

"""

DEMO_MESSAGE = """Ciao {{recipient.first_name}},
This is message from Bitcaster.

{{message}}

get Bitcaster...
"""


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true')
        parser.add_argument('--reset', action='store_true')

    def handle(self, *args, **options):  # noqa
        verbosity = options['verbosity']
        demo = options['demo']
        reset = options['reset']
        ModelUser = get_user_model()
        call_command('migrate', verbosity=verbosity - 1)

        if reset:
            from django.db import connection
            cursor = connection.cursor()
            for m in [Application, Subscription, Channel, ModelUser]:
                cursor.execute("TRUNCATE TABLE {} CASCADE".format(m._meta.db_table))

        if settings.DEBUG:
            pwd = '123'
        else:
            pwd = ModelUser.objects.make_random_password()

        admin, __ = ModelUser.objects.get_or_create(email='sax@saxix.org',
                                                    defaults=dict(is_superuser=True,
                                                                  is_staff=True,
                                                                  password=make_password(pwd)))

        self.stdout.write("Created superuser `sax` with password `{}`".format(pwd))

        org, __ = Organization.objects.get_or_create(name='bitcaster',
                                                     owner=admin)
        app, __ = Application.objects.get_or_create(name='Default Application',
                                                    organization=org)
        admin.tokens.create(application=app)
        env_file = str(settings.PROJECT_DIR / '.env')
        if not os.path.exists(env_file):
            self.stderr.write(""""{0} has not found.
 Environment file has not been found and a new empty one has been created.
 Fill it before launch this command again.
""".format(env_file))
            with open(env_file, "wb") as f:
                f.write(TEMPLATE_ENV)
            sys.exit(1)

        if demo:
            env = environ.Env(ENABLE_SENTRY=False)
            env_demo_file = str(settings.PROJECT_DIR / '.demo')
            if not os.path.exists(env_demo_file):
                self.stderr.write(""""{0} has not found.
 Environment file has not been found and a new empty one has been created.
 Fill it before launch this command again.
""".format(env_demo_file))
                with open(env_demo_file, "wb") as f:
                    f.write(TEMPLATE_DEMO)
                sys.exit(1)
            env.read_env(env_demo_file)

            def create_user(prefix):
                defs = dict(name=env(f'{prefix}_NAME'),
                            friendly_name=env(f'{prefix}_FRIENDLY_NAME'),
                            )
                u = User.objects.get_or_create(email=env(f'{prefix}_EMAIL'),
                                               defaults=defs)[0]
                u.set_password('123')
                u.save()
                org.add_member(u, Role.OWNER)
                return u

            def create_channel(handler):
                prefix = "CHANNEL__%s__" % handler.__module__.split('.')[0].replace('bitcaster_', '').upper()
                attrs = {k.replace(prefix, "").lower(): v for k, v in env.ENVIRON.items()
                         if k.startswith(prefix)}
                if not attrs:
                    sys.stderr.write(f"No valid configuration for {handler}")
                ok = handler.validate_configuration(attrs, False)
                return app.owned_channels.get_or_create(name=handler.name,
                                                        defaults=dict(
                                                            handler=fqn(handler),
                                                            enabled=ok,
                                                            config=attrs))[0]

            event, __ = app.events.get_or_create(name='Demo Event',
                                                 enabled=False,
                                                 defaults=dict(
                                                     arguments={'message': 'default_message'})
                                                 )

            msg, __ = event.messages.get_or_create(name='Demo Message',
                                                   defaults=dict(
                                                       subject='{{subject}}',
                                                       body=DEMO_MESSAGE)
                                                   )
            users = []

            if env('USER1_EMAIL'):
                user1 = create_user('USER1')
                user1.tokens.create()
                users.append(user1)
            else:
                self.stderr.write('set USER1_USERNAME in your env file')
                sys.exit(1)

            if env('USER2_EMAIL'):
                user2 = create_user('USER2')
                user2.tokens.create()
                users.append(user2)

            configured_channels = {"{1}".format(*k.split('__'))
                                   for k, v in env.ENVIRON.items() if k.startswith('CHANNEL__')}

            for name in configured_channels:
                try:
                    if name == "EMAIL":
                        plugin = "bitcaster.dispatchers.%s.%s" % (name.lower(), name.title())
                    else:
                        plugin = "bitcaster_%s.%s" % (name.lower(), name.title().replace('_', ''))
                    h = import_by_name(plugin)
                    ch = create_channel(h)
                    self.stdout.write(f"Created channel {ch}")
                    msg.channels.add(ch)
                    for i, user in enumerate(users, 1):
                        recipient = env.str(f'USER{i}_{name}', '')
                        if recipient:
                            cfg = {"recipient": recipient}
                            event.subscriptions.get_or_create(subscriber=user,
                                                              channel=ch,
                                                              active=False,
                                                              defaults={
                                                                  'config': cfg
                                                              })
                            self.stdout.write(f"    User {user} subscribed to {ch}")
                except ImportError as e:
                    self.stderr.write(f"{name} configuration found, but plugin not found. {e}")
                except Exception as e:
                    raise
