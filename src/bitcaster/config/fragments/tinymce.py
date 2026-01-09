# @ref https://django-tinymce.readthedocs.io/en/latest/installation.html#configuration

TINYMCE_DEFAULT_CONFIG = {
    "menubar": False,
    "plugins": "preview, code, lists, link, table",
    "license_key": "gpl",
    "toolbar": (
        "undo redo "
        " bold italic underline strikethrough "
        " numlist bullist checklist"
        " forecolor backcolor"
        " link table removeformat"
        " code"
        ""
    ),
}
