from typing import Any

from django.template import Context, Template


def render_string(content: str | None, context: dict[str, Any]) -> str:
    if not content:
        return ""
    tpl = Template(content)
    return str(tpl.render(Context(context)))
