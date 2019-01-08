import inspect
import re
from pathlib import Path
from urllib.parse import parse_qs

from django.conf import settings
from django.conf.urls import include
from django.contrib.admin import site
from django.contrib.staticfiles.views import serve as static_serve
from django.http import HttpResponse
from django.urls import path, re_path
from django.views.decorators.cache import cache_page
from django.views.static import serve
from django_sysinfo.views import admin_sysinfo, http_basic_login, sysinfo
from strategy_field.utils import import_by_name

import bitcaster.api.urls
import bitcaster.web.urls
from bitcaster.models import Channel


@cache_page(60 * 60 * 24)
def channel_icon(request, pk):
    ch = Channel.objects.get(pk=pk)
    return plugin_icon(request, ch.handler.fqn)


@cache_page(60 * 60 * 24)
def plugin_icon(request, fqn):
    h = import_by_name(fqn)
    loc = inspect.getfile(h)
    icon = Path(loc).parent / 'icon.png'
    try:
        image = icon.read_bytes()
    except (Exception, FileNotFoundError):
        icon = Path(str(settings.BITCASTER_DIR)) / 'assets/bitcaster/images/plugin.png'
        image = icon.read_bytes()
    return HttpResponse(image, content_type='image/png')


def oauth2callback(request):
    from bitcaster.models import Channel
    state = parse_qs(request.GET['state'])
    channel = Channel.objects.get(pk=state['channel'][0])
    return channel.handler.oauth_callback(request)


def static(prefix, view=serve, **kwargs):
    return re_path(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')),
                   view,
                   kwargs=kwargs)


urlpatterns = [path(r'api/', include(bitcaster.api.urls), name='api'),
               path(r'oauth2callback/', oauth2callback),
               path('admin/info/html/', admin_sysinfo, name='admin_info'),
               path('info/json/', http_basic_login(sysinfo), name='sys-info'),

               path('favicon.ico', serve, kwargs={'document_root': settings.STATIC_ROOT,
                                                  'path': 'favicon.ico'}),
               re_path('^admin/', site.urls),

               path('plugins/icons/channel/<int:pk>/', channel_icon, name='channel-icon'),
               path('plugins/icons/<str:fqn>/', plugin_icon, name='plugin-icon')]


handler404 = 'bitcaster.web.views.handler404'
handler500 = 'bitcaster.web.views.handler500'

if settings.DEBUG:
    urlpatterns += [static(settings.MEDIA_URL,
                           document_root=settings.MEDIA_ROOT,
                           show_indexes=True),
                    static(settings.STATIC_URL, static_serve,
                           # document_root=settings.STATIC_ROOT,
                           show_indexes=True, insecure=True)]
else:
    urlpatterns += [static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
                    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)]

urlpatterns += [path('', include(bitcaster.web.urls)), ]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path(r'__debug__/', include(debug_toolbar.urls)),
                   ] + urlpatterns
