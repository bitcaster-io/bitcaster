import re
from urllib.parse import parse_qs

import qrcode
from django.conf import settings
from django.conf.urls import include
from django.contrib.admin import site
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django_sysinfo.views import admin_sysinfo, http_basic_login, sysinfo

import bitcaster.api.urls
import bitcaster.web.urls


@csrf_exempt
def get_qrcode(request):
    text = request.GET['text']
    version = request.GET.get('version', 1)
    correction = request.GET.get('c', qrcode.constants.ERROR_CORRECT_M)
    size = request.GET.get('s', 8)

    qr = qrcode.QRCode(
        version=version,
        error_correction=correction,
        box_size=size,
        border=2,
    )
    qr.add_data(text)
    qr.make(fit=True)
    image = qr.make_image(fill_color='black', back_color='white')
    response = HttpResponse(content_type='image/png')
    image.save(response, 'PNG')
    return response


@csrf_exempt
def oauth2callback(request):
    from bitcaster.models import Channel
    state = parse_qs(request.GET['state'])
    channel = Channel.objects.get(pk=state['channel'][0])
    return channel.handler.oauth_callback(request)


@csrf_exempt
def channel_callback(request, pk):
    from bitcaster.models import Channel
    channel = Channel.objects.get(pk=pk)
    return channel.handler.callback(request)


@login_required
def channel_registration(request, pk):
    from bitcaster.models import Channel
    channel = Channel.objects.get(pk=pk)
    return channel.handler.registration(request)


urlpatterns = [path('api/', include(bitcaster.api.urls), name='api'),
               path('oauth2callback/', oauth2callback),
               path('channel-callback/<int:pk>/', channel_callback, name='channel-callback'),
               path('channel-registration/<int:pk>/', channel_registration, name='channel-registration'),
               path('qrcode/', get_qrcode, name='qrcode'),

               path('admin/info/html/', admin_sysinfo, name='admin_info'),
               path('info/json/', http_basic_login(sysinfo), name='sys-info'),

               path('favicon.ico', serve, kwargs={'document_root': settings.STATIC_ROOT,
                                                  'path': 'favicon.ico'}),
               path('admin/', site.urls),
               ]

handler400 = 'bitcaster.web.views.handler400'
handler403 = 'bitcaster.web.views.handler403'
handler404 = 'bitcaster.web.views.handler404'
handler500 = 'bitcaster.web.views.handler500'

urlpatterns += [re_path(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')),
                        serve, kwargs=dict(document_root=settings.MEDIA_ROOT,
                                           show_indexes=True))]

urlpatterns += [path('', include(bitcaster.web.urls)), ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path(r'__debug__/', include(debug_toolbar.urls)),
                   ] + urlpatterns

urlpatterns = [path(settings.URL_PREFIX, include(urlpatterns))]
