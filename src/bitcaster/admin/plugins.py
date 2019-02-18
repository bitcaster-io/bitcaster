from admin_extra_urls.extras import ExtraUrlMixin
from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from bitcaster.logging import getLogger
from bitcaster.models import DispatcherMetaData, MonitorMetaData

from .site import site

logger = getLogger(__name__)
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class PluginAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('fqn', 'version', 'is_core', 'enabled')
    list_editable = ('enabled',)


@admin.register(DispatcherMetaData, site=site)
class DispatcherMetaDataAdmin(PluginAdmin):
    pass


@admin.register(MonitorMetaData, site=site)
class MonitorMetaDataAdmin(PluginAdmin):
    pass
