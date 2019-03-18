from logging import getLogger

from admin_extra_urls.extras import ExtraUrlMixin, link
from django.contrib import admin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from bitcaster.models import AgentMetaData, DispatcherMetaData

from .site import site

logger = getLogger(__name__)
csrf_protect_m = method_decorator(csrf_protect)
sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


class PluginAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('fqn', 'version', 'is_core', 'enabled')
    list_editable = ('enabled',)

    def has_add_permission(self, request):
        return False

    @link()
    def inspect(self, request):
        self.model.objects.inspect()


@admin.register(DispatcherMetaData, site=site)
class DispatcherMetaDataAdmin(PluginAdmin):
    pass


@admin.register(AgentMetaData, site=site)
class AgentMetaDataAdmin(PluginAdmin):
    pass
