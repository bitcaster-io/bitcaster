from django.conf import settings
from django.urls import reverse

import bitcaster as app


def bitcaster(request):
    setup_url = ''
    if request.user.is_authenticated:
        membership = request.user.memberships.first()
        if membership:
            setup_url = reverse('org-dashboard', args=[membership.organization.slug])

    return {'bitcaster_version': app.get_full_version(settings.DEBUG),
            'setup_url': setup_url,
            'settings': settings,
            'ON_PREMISE': settings.ON_PREMISE,
            'git_status': app.get_git_status()
            }
