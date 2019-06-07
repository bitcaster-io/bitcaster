from django.contrib.auth.decorators import login_required
from django.core.cache import caches
from django.http import JsonResponse

from bitcaster.models import OrganizationMember
from bitcaster.security import ROLES

cache_lock = caches['lock']


@login_required()
def unlock(request, org, lock_name):
    user = OrganizationMember.objects.filter(organization__slug=org,
                                             user=request.user,
                                             role__in=[ROLES.OWNER,
                                                       ROLES.SUPERUSER]).first()
    if user:
        lock = cache_lock.lock(lock_name)
        ret = cache_lock.delete(lock.name)
        return JsonResponse({'key': lock_name, 'status': ret})
    return JsonResponse({'key': None, 'status': 'failed'}, 400)
