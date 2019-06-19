from django.contrib.auth.decorators import login_required
from django.core.cache import caches
from django.http import JsonResponse

from bitcaster.models import Occurence, OrganizationMember
from bitcaster.security import ORG_ROLES
from bitcaster.utils.locks import get_all_locks

cache_lock = caches['lock']


@login_required()
def lock_list(request, org):
    user = OrganizationMember.objects.filter(organization__slug=org,
                                             user=request.user,
                                             role__in=[ORG_ROLES.OWNER,
                                                       ORG_ROLES.SUPERUSER]).first()
    if user:
        locks = get_all_locks()
        return JsonResponse(locks)
    return JsonResponse({}, 400)


@login_required()
def unlock(request, org, pk):
    user = OrganizationMember.objects.filter(organization__slug=org,
                                             user=request.user,
                                             role__in=[ORG_ROLES.OWNER,
                                                       ORG_ROLES.SUPERUSER]).first()
    if user:
        ret = Occurence.objects.get(organization__slug=org,
                                    pk=pk).unlock()
        return JsonResponse({'key': pk, 'status': ret})
    return JsonResponse({'key': None, 'status': 'failed'}, 400)
