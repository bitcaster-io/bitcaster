from adminfilters.autocomplete import LinkedAutoCompleteFilter
from django.contrib import admin

from bitcaster.admin.base import BaseAdmin
from bitcaster.forms.media import MediaFileForm
from bitcaster.models import MediaFile


class MediaAdmin(BaseAdmin, admin.ModelAdmin[MediaFile]):
    list_display = ("name", "image", "size", "file_type", "mime_type")
    list_filter = (
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
    )
    autocomplete_fields = ("application", "project", "organization")
    form = MediaFileForm
