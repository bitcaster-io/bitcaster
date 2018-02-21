from urllib.parse import parse_qs

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path
from django_sysinfo.views import admin_sysinfo

import mercury.api.urls
import mercury.views
from mercury.admin import site


def oauth2callback(request):
    from mercury.models import Channel
    state = parse_qs(request.GET['state'])
    channel = Channel.objects.get(pk=state['channel'][0])
    return channel.handler.oauth_callback(request)


urlpatterns = [url(r'^api/', include(mercury.api.urls), name='api'),
               url('oauth2callback/$', oauth2callback),
               url('^', site.urls),
               path("info/", admin_sysinfo, name="admin_info"),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
