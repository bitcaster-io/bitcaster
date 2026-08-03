from typing import Any

import re
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.core import checks

from .links import HELP_LINKS

E001 = checks.Error(
    "Doc path '%s' does not resolve to an existing source page under docs/",
    id="bitcaster.help.E001",
)

E002 = checks.Error(
    "Doc path '%s' is not a valid relative path (no leading slash, no '#', no '.md')",
    id="bitcaster.help.E002",
)

E003 = checks.Error(
    "Help link regex '%s' is invalid: %s",
    id="bitcaster.help.E003",
)


def _validate_doc_path(doc_path: str, docs_root: Path) -> list[checks.CheckMessage]:
    if doc_path.startswith("/") or "#" in doc_path or doc_path.endswith(".md"):
        return [checks.Error(E002.msg % doc_path, id=E002.id)]
    page = doc_path.rstrip("/")
    leaf = docs_root / f"{page}.md"
    section = docs_root / page
    if leaf.is_file():
        return []
    if section.is_dir() and ((section / ".pages").is_file() or (section / "index.md").is_file()):
        return []
    return [checks.Error(E001.msg % doc_path, id=E001.id)]


@checks.register("help")
def check_help_links(app_configs: AppConfig, **kwargs: Any) -> list[checks.CheckMessage]:
    errors: list[checks.CheckMessage] = []
    docs_root = Path(settings.PROJECT_ROOT) / "docs"
    if not docs_root.is_dir():
        return errors
    for pattern, doc_path in HELP_LINKS.items():
        try:
            re.compile(pattern)
        except re.error as e:
            errors.append(checks.Error(E003.msg % (pattern, e), id=E003.id))
            continue
        errors.extend(_validate_doc_path(doc_path, docs_root))
    return errors
