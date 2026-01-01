from typing import Any

from django import forms
from django.db.models import Model
from smart_selects.widgets import ChainedSelect
from unfold import widgets
from unfold.forms import AdminForm
from unfold.widgets import (
    SELECT_CLASSES,
    UnfoldAdminFileFieldWidget,
    UnfoldAdminIntegerFieldWidget,
    UnfoldAdminSelect2Widget,
    UnfoldAdminSelectWidget,
    UnfoldAdminTextInputWidget,
    UnfoldBooleanSwitchWidget,
)

from bitcaster.dispatchers.base import DispatcherConfig

__all__ = [
    "UnfoldAdminTextInputWidget",
    "UnfoldAdminSelect2Widget",
    "UnfoldAdminSelectWidget",
    "UnfoldAdminFileFieldWidget",
    "UnfoldBooleanSwitchWidget",
    "UnfoldAdminIntegerFieldWidget",
]

WIDGETS_OVERRIDES = {
    forms.DateField: widgets.UnfoldAdminSingleDateWidget,
    forms.EmailField: widgets.UnfoldAdminEmailInputWidget,
    forms.CharField: widgets.UnfoldAdminTextInputWidget,
    forms.SlugField: widgets.UnfoldAdminTextInputWidget,
    forms.URLField: widgets.UnfoldAdminURLInputWidget,
    forms.GenericIPAddressField: widgets.UnfoldAdminTextInputWidget,
    forms.UUIDField: widgets.UnfoldAdminUUIDInputWidget,
    forms.TextInput: widgets.UnfoldAdminTextareaWidget,
    forms.NullBooleanField: widgets.UnfoldAdminNullBooleanSelectWidget,
    forms.BooleanField: widgets.UnfoldBooleanSwitchWidget,
    forms.IntegerField: widgets.UnfoldAdminIntegerFieldWidget,
    forms.DecimalField: widgets.UnfoldAdminDecimalFieldWidget,
    forms.FloatField: widgets.UnfoldAdminDecimalFieldWidget,
    forms.FileField: widgets.UnfoldAdminFileFieldWidget,
    forms.ImageField: widgets.UnfoldAdminImageFieldWidget,
}


# kudos to https://github.com/unfoldadmin/django-unfold/issues/180
class UnfoldForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if widget := WIDGETS_OVERRIDES.get(field.__class__):
                field.widget = widget()


# kudos to https://github.com/unfoldadmin/django-unfold/issues/180
class UnfoldAdminForm(AdminForm):
    def __init__(
        self,
        form: forms.ModelForm[Model] | DispatcherConfig,
        fieldsets: list[tuple[str | None, dict[str, Any]]],
        prepopulated_fields: dict[str, list[str]] | None,
        readonly_fields: list[str] | None = None,
        model_admin: "Any | None" = None,
    ) -> None:
        super().__init__(form, fieldsets, prepopulated_fields, readonly_fields, model_admin)
        for field in self.form.fields.values():
            if widget := WIDGETS_OVERRIDES.get(field.__class__):
                field.widget = widget()


class UnfoldChainedSelect(ChainedSelect):
    template_name = "unfold/widgets/select.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "attrs" not in kwargs:
            kwargs["attrs"] = {}

        attrs = kwargs["attrs"]
        attrs["class"] = " ".join([*SELECT_CLASSES, attrs.get("class", "") if attrs else ""])

        super().__init__(*args, **kwargs)
