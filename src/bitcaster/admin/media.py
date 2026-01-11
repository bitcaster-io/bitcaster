from adminfilters.autocomplete import LinkedAutoCompleteFilter
from unfold.admin import ModelAdmin as UnfoldModelAdmin  # noqa

from bitcaster.admin.base import BaseAdmin, BitcasterModelAdmin
from bitcaster.forms.media import MediaFileForm
from bitcaster.models import MediaFile


class MediaFileAdmin(BaseAdmin, BitcasterModelAdmin[MediaFile]):
    list_display = ("name", "image", "size", "file_type", "mime_type")
    list_filter = (
        ("application__project__organization", LinkedAutoCompleteFilter.factory(parent=None)),
        ("application__project", LinkedAutoCompleteFilter.factory(parent="application__project__organization")),
        ("application", LinkedAutoCompleteFilter.factory(parent="application__project")),
    )
    autocomplete_fields = ("application", "project", "organization")
    form = MediaFileForm
