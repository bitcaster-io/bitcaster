from urllib.parse import parse_qs

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path
from django_sysinfo.views import admin_sysinfo, http_basic_login, sysinfo

import mercury.api.urls
import mercury.views
from mercury.admin import site


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
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
