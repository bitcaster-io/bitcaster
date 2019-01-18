from admin_extra_urls.extras import ExtraUrlMixin
from django.contrib import admin

from bitcaster.models.configurationissue import ConfigurationIssue

from .site import site


@admin.register(ConfigurationIssue, site=site)
class ConfigurationIssueAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('organization', 'application', 'level', 'section')
    list_filter = ('organization', 'application', 'level', 'section')
