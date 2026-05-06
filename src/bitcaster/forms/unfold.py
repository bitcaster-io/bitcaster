from typing import Any

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

from django import forms
from django.db.models import Model

from ..dispatchers.base import DispatcherConfig

__all__ = [
    "UnfoldAdminTextInputWidget",
    "UnfoldAdminSelect2Widget",
    "UnfoldAdminSelectWidget",
    "UnfoldAdminFileFieldWidget",
    "UnfoldBooleanSwitchWidget",
    "UnfoldAdminIntegerFieldWidget",
]

WIDGETS_OVERRIDES = {
    forms.BooleanField: widgets.UnfoldBooleanSwitchWidget,
    forms.ChoiceField: widgets.UnfoldAdminSelectWidget,
    forms.TypedChoiceField: widgets.UnfoldAdminSelectWidget,
    forms.CharField: widgets.UnfoldAdminTextInputWidget,
    forms.DateField: widgets.UnfoldAdminSingleDateWidget,
    forms.DecimalField: widgets.UnfoldAdminDecimalFieldWidget,
    forms.EmailField: widgets.UnfoldAdminEmailInputWidget,
    forms.FileField: widgets.UnfoldAdminFileFieldWidget,
    forms.FloatField: widgets.UnfoldAdminDecimalFieldWidget,
    forms.GenericIPAddressField: widgets.UnfoldAdminTextInputWidget,
    forms.ImageField: widgets.UnfoldAdminImageFieldWidget,
    forms.IntegerField: widgets.UnfoldAdminIntegerFieldWidget,
    forms.NullBooleanField: widgets.UnfoldAdminNullBooleanSelectWidget,
    forms.SlugField: widgets.UnfoldAdminTextInputWidget,
    forms.Textarea: widgets.UnfoldAdminTextareaWidget,
    forms.URLField: widgets.UnfoldAdminURLInputWidget,
    forms.UUIDField: widgets.UnfoldAdminUUIDInputWidget,
    # forms.ModelChoiceField: widgets.UnfoldAdminSelect2Widget,
}


# kudos to https://github.com/unfoldadmin/django-unfold/issues/180
class UnfoldForm(forms.Form):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.HiddenInput):
                continue

            for field_class, widget in WIDGETS_OVERRIDES.items():
                if isinstance(field, field_class):
                    if isinstance(field.widget, forms.Textarea):
                        field.widget = widgets.UnfoldAdminTextareaWidget()
                    elif hasattr(field, "choices"):
                        field.widget = widget()
                        field.widget.choices = field.choices
                    else:
                        field.widget = widget()
                    break


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
        for field_name, field in self.form.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue

            for field_class, widget in WIDGETS_OVERRIDES.items():
                if isinstance(field, field_class):
                    if isinstance(field.widget, forms.PasswordInput):
                        value = self.form.initial.get(field_name)
                        field.widget = widgets.UnfoldAdminPasswordWidget({"value": value})
                    elif isinstance(field.widget, forms.Textarea):
                        field.widget = widgets.UnfoldAdminTextareaWidget()
                    elif hasattr(field, "choices"):
                        field.widget.choices = field.choices
                    else:
                        field.widget = widget()
                    break


class UnfoldChainedSelect(ChainedSelect):
    template_name = "unfold/widgets/select.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "attrs" not in kwargs:
            kwargs["attrs"] = {}

        attrs = kwargs["attrs"]
        attrs["class"] = " ".join([*SELECT_CLASSES, attrs.get("class", "") if attrs else ""])

        super().__init__(*args, **kwargs)
