import re
from urllib.parse import parse_qs

from django.conf import settings
from django.conf.urls import include
from django.contrib.admin import site
from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django_sysinfo.views import admin_sysinfo, http_basic_login, sysinfo

import bitcaster.api.urls
import bitcaster.web.urls


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


urlpatterns = [path('api/', include(bitcaster.api.urls), name='api'),
               path('oauth2callback/', oauth2callback),
               path('channel-callback/<int:pk>/', channel_callback, name='channel-callback'),
               path('admin/info/html/', admin_sysinfo, name='admin_info'),
               path('info/json/', http_basic_login(sysinfo), name='sys-info'),

               path('favicon.ico', serve, kwargs={'document_root': settings.STATIC_ROOT,
                                                  'path': 'favicon.ico'}),
               path('admin/', site.urls),
               ]

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
