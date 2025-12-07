from django.contrib.admin import ModelAdmin
from django.db.models import Model


class MultiModelAdmin(ModelAdmin[Model]):
    def get_changelist(self, request, **kwargs):
        from .changelist import MultiAdminChangeList

        return MultiAdminChangeList
