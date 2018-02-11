import os
import sys
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management import call_command
from django.core.management.base import BaseCommand

import environ
from strategy_field.utils import fqn, import_by_name

from mercury.dispatchers import Gmail
from mercury.models import Application, Channel, Subscription, User

TEMPLATE = b"""
ADMIN_EMAIL=
DEBUG=True
DATABASE_URL=psql://postgres:@127.0.0.1:5432/mercury
MERCURY_SECRET_KEY=123

USER1_USERNAME=
USER1_FIRST_NAME=
USER1_LAST_NAME=
USER1_EMAIL=
USER1_WHATSAPP=
USER1_TWILIO=
USER1_SLACK=

USER2_USERNAME=
USER2_FIRST_NAME=
USER2_LAST_NAME=
USER2_EMAIL=
USER2_WHATSAPP=
USER2_TWILIO=
USER2_SLACK

; create password at https://myaccount.google.com/apppasswords
CHANNEL_GMAIL_USER=
CHANNEL_GMAIL_PASSWORD=
CHANNEL_GMAIL_SENDER=mercury@noreply.org

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
"""

DEMO_MESSAGE = """Ciao {{recipient.first_name}},
This is message from Mercury.

{{message}}

get Mercury...
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
                # m.objects.all().delete()

        if settings.DEBUG:
            pwd = '123'
        else:
            pwd = ModelUser.objects.make_random_password()

        admin, __ = ModelUser.objects.get_or_create(username='sax',
                                                    defaults=dict(is_superuser=True,
                                                                  is_staff=True,
                                                                  password=make_password(pwd)))

        self.stdout.write("Created superuser `sax` with password `{}`".format(pwd))

        app, __ = Application.objects.get_or_create(name='Default Application',
                                                    owner=admin,
                                                    )
        admin.tokens.create(application=app)

        if demo:
            env = environ.Env(ENABLE_SENTRY=False)
            env_file = str(settings.PROJECT_DIR.path('.demo'))
            if not os.path.exists(env_file):
                self.stderr.write(""""{0} has not found.
 Environment file has not been found and a new empty one has been created.
 Fill it before launch this command again.
""".format(env_file))
                with open(env_file, "wb") as f:
                    f.write(TEMPLATE)
                sys.exit(1)
            env.read_env(env_file)

            def create_user(prefix):
                uname = env(f'{prefix}_USERNAME')
                defs = dict(first_name=env(f'{prefix}_FIRST_NAME'),
                            last_name=env(f'{prefix}_LAST_NAME'),
                            email=env(f'{prefix}_EMAIL')
                            )
                return User.objects.get_or_create(username=uname,
                                                  defaults=defs)[0]

            def create_channel(handler):
                prefix = "CHANNEL_%s_" % handler.name.upper()
                attrs = {k.replace(prefix, "").lower(): v for k, v in env.ENVIRON.items()
                         if k.startswith(prefix)}

                return app.owned_channels.get_or_create(name=handler.name,
                                                        defaults=dict(
                                                            handler=fqn(handler),
                                                            enabled=True,
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

            ch_gmail = create_channel(Gmail)
            msg.channels.add(ch_gmail)

            users = []

            if env('USER1_USERNAME'):
                user1 = create_user('USER1')
                user1.tokens.create()
                event.subscriptions.get_or_create(subscriber=user1,
                                                  active=False,
                                                  channel=ch_gmail)
                users.append(user1)
            else:
                self.stderr.write('set USER1_USERNAME in your env file')
                sys.exit(1)

            if env('USER2_USERNAME'):
                user2 = create_user('USER2')
                user2.tokens.create()
                event.subscriptions.get_or_create(subscriber=user2,
                                                  active=False,
                                                  channel=ch_gmail)
                users.append(user2)

            for plugin in ['mercury_slack.Slack',
                           'mercury_twilio.Twilio'
                           ]:
                try:
                    h = import_by_name(plugin)
                    ch = create_channel(h)
                    self.stdout.write(f"Create channel {ch}")
                    prefix = ch.name.upper()
                    msg.channels.add(ch)
                    for i, user in enumerate(users, 1):
                        cfg = {"recipient": env(f'USER{i}_{prefix}')}
                        s = event.subscriptions.get_or_create(subscriber=user,
                                                              channel=ch,
                                                              active=False,
                                                              config=cfg)[0]
                    self.stdout.write(f"Create subscription {s}")
                except ImportError:
                    pass
