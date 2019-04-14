from django.apps import AppConfig


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


def log_login(sender, user, request, **kwargs):
    from bitcaster.models.audit import AuditLogEntry

    AuditLogEntry.objects.create(event=AuditLogEntry.AuditEvent.MEMBER_LOGIN,
                                 actor=user,
                                 )


def log_logout(sender, user, request, **kwargs):
    from bitcaster.models.audit import AuditLogEntry

    AuditLogEntry.objects.create(event=AuditLogEntry.AuditEvent.MEMBER_LOGOUT,
                                 actor=user)
