from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django.views.decorators.cache import cache_page

from bitcaster.models import Organization
from bitcaster.tsdb.api import get_data, stats
from bitcaster.utils.ttl import HOUR


def parse_time(dt, tz):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def audit_log(request, org):
    today = datetime.now()
    organization = Organization.objects.get(slug=org)
    data = organization.auditlog \
        .filter(timestamp__lte=today, timestamp__gt=today - timedelta(days=30)) \
        .extra(select={'t': "TO_CHAR( timestamp, 'YYYY-MM-DD' )"}) \
        .values('t') \
        .annotate(y=Count('timestamp')) \
        .order_by('t')
    return JsonResponse(list(data), safe=False)


@cache_page(HOUR)
@login_required
def error_log(request, org):
    data = []
    # o = Organization.objects.get(slug=org)
    # data = stats.error.get_data(o.pk, target='organization', granularity='h')
    return JsonResponse([dict(t=parse_time(e[0], request.user.timezone),
                              y=e[1]) for e in data], safe=False)


# @login_required
# @cache_page(HOUR)
def occurence_log(request, org):
    # o = Organization.objects.get(slug=org)
    # data = o.stats.get_data(metric='org:%s' % org, granularity='h')
    # data = Occurence.stats.get_data(metric='org:%s' % org, granularity='h')
    # data = stats.occurence.get_data(o.pk, target='organization', granularity='h')
    data = get_data('occurence', 'h')
    return JsonResponse([dict(t=parse_time(e[0], request.user.timezone),
                              y=e[1]) for e in data], safe=False)


# @login_required
# @cache_page(HOUR)
def notification_log(request, org):
    # o = Organization.objects.get(slug=org)
    # data = stats.notification.get_data(o.pk, target='organization', granularity='h')
    data = get_data('notification', 'h')
    return JsonResponse([dict(t=parse_time(e[0], request.user.timezone),
                              y=e[1]) for e in data], safe=False)


# @login_required
# @cache_page(HOUR)
def get_buffers(request, org, name):
    # o = Organization.objects.get(slug=org)
    # data = buffers.get('%s:organization' % name)
    data = stats.get_data(name)
    return JsonResponse({'value': int(data.decode('utf8'))})


def trigger_task(request, task_fqn):
    try:
        f = import_string(task_fqn)
        f.delay()
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=401)
    return JsonResponse({'message': 'Ok'}, status=200)
