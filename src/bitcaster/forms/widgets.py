from typing import TYPE_CHECKING, Any, Optional

from django.contrib.admin import AdminSite
from django.contrib.admin.widgets import AutocompleteSelect

if TYPE_CHECKING:
    from django.forms.widgets import _OptAttrs


class AutocompletSelectEnh(AutocompleteSelect):
    def __init__(
        self,
        field: Any,
        admin_site: AdminSite,
        attrs: "Optional[_OptAttrs]" = None,
        choices: Any = (),
        using: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.exclude = kwargs.pop("exclude", {})
        self.filter = kwargs.pop("filter", {})
        super().__init__(field, admin_site, attrs, choices, using)

    def get_url(self) -> str:
        args = [f"{k}={v} " for k, v in self.filter.items()]
        args.extend([f"{k}__not={v}" for k, v in self.exclude.items()])
        query_string = "&".join(args)
        return f"{super().get_url()}?{query_string}"
