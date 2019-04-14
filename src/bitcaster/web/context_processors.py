from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

import bitcaster as app
from bitcaster.config.environ import env
from bitcaster.messages import DEFAULT_LEVELS


class EnvWrapper:
    def __init__(self, environ):
        self.environ = environ

    def __getattr__(self, item):
        try:
            return self.environ(item)
        except ImproperlyConfigured:
            return None


def bitcaster(request):
    setup_url = ''
    if request.user.is_authenticated:
        membership = request.user.memberships.first()
        if membership:
            setup_url = reverse('org-dashboard', args=[membership.organization.slug])

    return {'bitcaster_version': app.get_full_version(settings.DEBUG),
            'setup_url': setup_url,
            'settings': settings,
            'env': EnvWrapper(env),
            'git_status': app.get_git_status()
            }


def messages(request):
    """
    Return a lazy 'messages' context variable as well as
    'DEFAULT_MESSAGE_LEVELS'.
    """
    return {
        'messages': getattr(request, '_messages', []),
        'alarms': getattr(request, '_alarms', []),
        'DEFAULT_MESSAGE_LEVELS': DEFAULT_LEVELS,
    }
