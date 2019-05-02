from datetime import datetime, timedelta

import pytz
from django.db.models import Count
from django.http import JsonResponse

from bitcaster.models import Notification, Organization


def audit_log(request, org):
    today = datetime.now().replace(tzinfo=pytz.UTC).date()
    organization = Organization.objects.get(slug=org)
    data = organization.auditlog \
        .filter(timestamp__lte=today, timestamp__gt=today - timedelta(days=30)) \
        .extra(select={'t': "TO_CHAR( timestamp, 'YYYY-MM-DD' )"}) \
        .values('t') \
        .annotate(y=Count('timestamp')) \
        .order_by('t')
    return JsonResponse(list(data), safe=False)


def occurence_log(request, org):
    today = datetime.now().replace(tzinfo=pytz.UTC).date()
    organization = Organization.objects.get(slug=org)
    data = organization.occurences \
        .filter(timestamp__lte=today, timestamp__gt=today - timedelta(days=30)) \
        .extra(select={'t': "TO_CHAR( timestamp, 'YYYY-MM-DD' )"}) \
        .values('t') \
        .annotate(y=Count('timestamp')) \
        .order_by('t')
    return JsonResponse(list(data), safe=False)


def notification_log(request, org):
    today = datetime.now().replace(tzinfo=pytz.UTC).date()
    organization = Organization.objects.get(slug=org)
    data = Notification.objects.filter(application__organization=organization,
                                       timestamp__lte=today, timestamp__gt=today - timedelta(days=30)) \
        .extra(select={'t': "TO_CHAR( timestamp, 'YYYY-MM-DD' )"}) \
        .values('t') \
        .annotate(y=Count('timestamp')) \
        .order_by('t')
    return JsonResponse(list(data), safe=False)
