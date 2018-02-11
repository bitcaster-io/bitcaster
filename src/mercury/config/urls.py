from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from django_sysinfo.views import admin_sysinfo

import mercury.api.urls
import mercury.views

urlpatterns = [url(r'^api/', include(mercury.api.urls), name='api'),
               url('^', admin.site.urls),
               path("info/", admin_sysinfo, name="admin_info"),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
