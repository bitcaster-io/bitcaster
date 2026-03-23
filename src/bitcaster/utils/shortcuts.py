from typing import Any

from django.template import Context, Template


def render_message(content: str | None, context: dict[str, Any]) -> str:
    if not content:
        return ""

    tpl = Template("%s%s" % ("{% load bitcaster attachments %}", content))
    return str(tpl.render(Context(context)))
