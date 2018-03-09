from django.conf import settings

import bitcaster as app


def bitcaster(request):
    return {'bitcaster_version': app.get_full_version(settings.DEBUG),
            'git_status': app.get_git_status(settings.DEBUG)
            }
