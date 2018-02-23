import inspect
from pathlib import Path
from urllib.parse import parse_qs

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path, re_path
from django_sysinfo.views import admin_sysinfo, http_basic_login, sysinfo
from strategy_field.utils import import_by_name

import mercury.api.urls
import mercury.views
from mercury.admin import site


def plugin_icon(request, fqn):
    h = import_by_name(fqn)
    loc = inspect.getfile(h)
    icon = Path(loc).parent / 'icon.png'
    try:
        return HttpResponse(icon.read_bytes(), content_type='image/png')
    except FileNotFoundError:
        icon = Path(str(settings.MERCURY_DIR)) / 'static/plugin.png'
        return HttpResponse(icon.read_bytes(), content_type='image/png')


def oauth2callback(request):
    from mercury.models import Channel
    state = parse_qs(request.GET['state'])
    channel = Channel.objects.get(pk=state['channel'][0])
    return channel.handler.oauth_callback(request)


urlpatterns = [path(r'api/', include(mercury.api.urls), name='api'),
               path(r'oauth2callback/', oauth2callback),
               # path(r'sys/', include(django_sysinfo.urls)),
               path('admin/info/html/', admin_sysinfo, name="admin_info"),
               path('info/json/', http_basic_login(sysinfo), name="sys-info"),

               path('', site.urls),
               re_path('plugins/icon/(?P<fqn>.*)', plugin_icon, name="plugin-icon"),

               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
