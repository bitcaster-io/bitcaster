from datetime import datetime, timedelta

from django.db.models import Count
from django.http import JsonResponse

from bitcaster.models import Organization
from bitcaster.tsdb.db import stats


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


def error_log(request, org):
    data = stats.get_data(org, 'error', 'h')
    return JsonResponse([dict(t=parse_time(e[0], request.user.timezone),
                              y=e[1]) for e in data], safe=False)


def occurence_log(request, org):
    data = stats.get_data(org, 'occurence', 'h')
    return JsonResponse([dict(t=parse_time(e[0], request.user.timezone),
                              y=e[1]) for e in data], safe=False)


def notification_log(request, org):
    data = stats.get_data(org, 'notification', 'h')
    return JsonResponse([dict(t=parse_time(e[0], request.user.timezone),
                              y=e[1]) for e in data], safe=False)
