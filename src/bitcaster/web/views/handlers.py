from django.conf import settings
from django.shortcuts import render
from sentry_sdk import capture_exception

from bitcaster.utils.language import repr_list


def handler400(request, *args, **kwargs):
    response = render(request, 'bitcaster/400.html')
    response.status_code = 400
    return response


def handler403(request, *args, **kwargs):
    exc = kwargs['exception']
    id = capture_exception(exc)
    data = {'event_id': id,
            'code': 403,
            'settings': settings,
            'referer': request.META.get('HTTP_REFERER', '/'),
            'title': 'FORBIDDEN',
            'description': 'The client has insufficient authentication credentials '
                           'for the server to process this request.'}
    if hasattr(exc, 'view'):
        data['permissions'] = repr_list(exc.view.permissions)
    return render(request, 'bitcaster/403.html', data)


def handler404(request, *args, **kwargs):
    response = render(request, 'bitcaster/404.html')
    response.status_code = 404
    return response


def handler500(request, *args, **kwargs):
    response = render(request, 'bitcaster/500.html', {})
    response.status_code = 500
    return response
