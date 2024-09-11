from constance.admin import Config
from constance.admin import ConstanceAdmin as _ConstanceAdmin
from flags.admin import FlagStateAdmin as _FlagStateAdmin
from flags.models import FlagState

__all__ = ["ConstanceAdmin", "Config", "FlagStateAdmin", "FlagState"]

from flags.state import flag_enabled


class ConstanceAdmin(_ConstanceAdmin):
    pass


class FlagStateAdmin(_FlagStateAdmin):
    search_fields = ("name",)
    list_display = ("name", "condition", "value", "required", "active")
    ordering = ("name",)
    list_filter = ("condition", "required")

    def active(self, obj: FlagState) -> bool:
        return flag_enabled(obj.name)

    active.boolean = True
