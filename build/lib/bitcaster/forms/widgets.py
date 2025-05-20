from typing import TYPE_CHECKING, Any

from django.contrib.admin import AdminSite
from django.contrib.admin.widgets import AutocompleteSelect
from django_select2.forms import Select2TagWidget

if TYPE_CHECKING:
    from django.forms.utils import _DataT, _FilesT
    from django.forms.widgets import _OptAttrs
    from django.utils.choices import _Choices


class EnvironmentWidget(Select2TagWidget):
    choices: "_Choices"

    def value_from_datadict(self, data: "_DataT", files: "_FilesT", name: str) -> str:
        values = super().value_from_datadict(data, files, name)
        return ",".join(values)

    def optgroups(self, name: str, value: str, attrs: Any = None) -> list[tuple[str, Any]]:
        if not self.choices and value:
            self.choices = [(c, c) for c in value]
        return super().optgroups(name, value, attrs=None)


class AutocompletSelectEnh(AutocompleteSelect):
    def __init__(
        self,
        field: Any,
        admin_site: AdminSite,
        attrs: "_OptAttrs | None" = None,
        choices: Any = (),
        using: str | None = None,
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
