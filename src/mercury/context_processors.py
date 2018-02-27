from django.conf import settings

import mercury


def bitcaster(request):
    return {'bitcaster_version': mercury.get_full_version(settings.DEBUG),
            'git_status': mercury.get_git_status(settings.DEBUG)
            }
