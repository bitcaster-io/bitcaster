import pytest
from django.contrib import admin
from django.db import models


@pytest.mark.django_db
def test_admin_autocomplete_fields():
    """
    Test generic to ensure all ForeignKey and ManyToManyField in ModelAdmin
    are using autocomplete_fields, unless they are readonly or have a custom widget.
    """
    errors = []

    from django.test import RequestFactory

    from bitcaster.models import User

    rf = RequestFactory()
    request = rf.get("/")
    request.user = User(is_superuser=True, is_staff=True)

    for model, model_admin in admin.site._registry.items():
        if not hasattr(model, "_meta") or not hasattr(model._meta, "get_fields"):
            continue

        # Get all relational fields for the model
        relational_fields = [
            f.name for f in model._meta.get_fields() if isinstance(f, (models.ForeignKey, models.ManyToManyField))
        ]

        # Get the form used by the admin to check for custom widgets
        try:
            form_class = model_admin.get_form(request)
            form_instance = form_class()
        except Exception:
            # If we cannot instantiate the form, skip widget check for this model
            form_instance = None

        # Fields that are allowed to NOT be in autocomplete_fields
        exempt_fields = set()
        exempt_fields.update(model_admin.get_readonly_fields(request))
        exempt_fields.update(model_admin.raw_id_fields or [])
        exempt_fields.update((model_admin.radio_fields or {}).keys())
        exempt_fields.update(model_admin.filter_horizontal or [])
        exempt_fields.update(model_admin.filter_vertical or [])

        # Check for custom autocomplete widgets in the form
        if form_instance:
            from unfold.widgets import UnfoldAdminSelect2Widget, UnfoldAdminSelectWidget

            from bitcaster.forms.unfold import UnfoldChainedSelect

            for field_name, field in form_instance.fields.items():
                if isinstance(field.widget, (UnfoldAdminSelect2Widget, UnfoldAdminSelectWidget, UnfoldChainedSelect)):
                    exempt_fields.add(field_name)

        # BitcasterModelAdmin automatically uses UnfoldAdminSelectWidget for all ForeignKeys
        from bitcaster.admin.base import BitcasterModelAdmin

        is_bitcaster_admin = isinstance(model_admin, BitcasterModelAdmin)

        # Check if the field is actually displayed in the admin
        display_fields = set()
        if model_admin.fields:
            display_fields.update(model_admin.fields)
        if model_admin.fieldsets:
            for _, fieldset_options in model_admin.fieldsets:
                if "fields" in fieldset_options:
                    for field in fieldset_options["fields"]:
                        if isinstance(field, (list, tuple)):
                            display_fields.update(field)
                        else:
                            display_fields.add(field)

        # If neither fields nor fieldsets are defined, Django shows all non-auto fields
        # but for this test we focus on what's explicitly or implicitly visible.
        # If both are empty, we assume all relational fields might be visible.
        check_fields = relational_fields
        if display_fields:
            check_fields = [f for f in relational_fields if f in display_fields]

        autocomplete_fields = model_admin.get_autocomplete_fields(None) or []

        errors.extend(
            [
                (
                    f"Admin '{model_admin.__class__.__name__}' for model '{model.__name__}' "
                    f"has relational field '{field_name}' but it's not in autocomplete_fields."
                )
                for field_name in check_fields
                if field_name not in autocomplete_fields
                and field_name not in exempt_fields
                and not (is_bitcaster_admin and isinstance(model._meta.get_field(field_name), models.ForeignKey))
            ]
        )

    if errors:
        pytest.fail("\n".join(errors))
