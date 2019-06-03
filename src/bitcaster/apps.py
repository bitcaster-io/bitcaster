from django.apps import AppConfig
from django.core.signals import got_request_exception
from django.db import ProgrammingError

from bitcaster.state import state


class Config(AppConfig):
    name = 'bitcaster'

    def ready(self):
        from .config.environ import env  # noqa
        from . import celery  # noqa
        from django.conf import settings  # noqa
        from .dispatchers.registry import dispatcher_registry  # noqa
        from .agents.registry import agent_registry  # noqa
        from . import tasks  # noqa
        from . import checks  # noqa
        from django.contrib.auth.signals import user_logged_in, user_logged_out

        user_logged_in.connect(log_login)
        user_logged_out.connect(log_logout)
        from bitcaster.models import Organization
        try:
            state.data['organization'] = Organization.objects.first()
        except ProgrammingError:
            pass

        got_request_exception.connect(capture_exception)


def capture_exception(sender, request, **kwargs):
    from crashlog.middleware import process_exception
    process_exception(sender, request, message_user=False)


def log_login(sender, user, request, **kwargs):
    from bitcaster.models.audit import AuditLogEntry, AuditEvent
    membership = user.memberships.first()
    AuditLogEntry.objects.create(event=AuditEvent.MEMBER_LOGIN,
                                 actor=user,
                                 organization=membership.organization,
                                 )


def log_logout(sender, user, request, **kwargs):
    from bitcaster.models.audit import AuditLogEntry, AuditEvent
    membership = user.memberships.first()
    AuditLogEntry.objects.create(event=AuditEvent.MEMBER_LOGOUT,
                                 organization=membership.organization,
                                 actor=user)
