from django.conf import settings
from django.urls import reverse

import bitcaster as app
from bitcaster.messages import DEFAULT_LEVELS


def bitcaster(request):
    setup_url = ''
    if request.user.is_authenticated:
        membership = request.user.memberships.first()
        if membership:
            setup_url = reverse('org-dashboard', args=[membership.organization.slug])

    return {'bitcaster_version': app.get_full_version(settings.DEBUG),
            'setup_url': setup_url,
            'settings': settings,
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
