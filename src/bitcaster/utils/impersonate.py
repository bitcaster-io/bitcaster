from constance import config
from django.http import Http404
from impersonate.decorators import allowed_user_required
from impersonate.views import impersonate, stop_impersonate

from bitcaster.models import User


def queryset(request):
    return User.objects.exclude(id=request.user.id).exclude(is_superuser=True).order_by('email')


@allowed_user_required
def impersonate_start(request, uid):
    if not config.ENABLE_IMPERSONATE:
        raise Http404
    return impersonate(request, uid)


def impersonate_stop(request):
    return stop_impersonate(request)
