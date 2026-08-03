# mypy: disable-error-code="attr-defined"
from typing import Any

from pytest_django.fixtures import SettingsWrapper

from django.template import Context, Template
from django.test import RequestFactory


def _render(path: str, **ctx: Any) -> str:
    t = Template("{% load help %}{% help %}")
    context = Context({"request": RequestFactory().get(path), **ctx})
    return t.render(context)


def test_renders_complete_link() -> None:
    out = _render("/admin/bitcaster/application/")
    assert 'href="https://docs.bitcaster.io/adm-guide/app/"' in out
    assert 'target="_blank"' in out
    assert 'rel="noopener"' in out
    assert '<span class="material-symbols-outlined">help</span>' in out
    assert 'title="Documentation"' in out
    assert 'aria-label="Documentation"' in out


def test_renders_nothing_for_unmapped_path() -> None:
    assert _render("/") == ""


def test_renders_nothing_without_request() -> None:
    t = Template("{% load help %}{% help %}")
    assert t.render(Context({})) == ""


def test_renders_nothing_for_empty_doc_site(settings: SettingsWrapper) -> None:
    settings.BITCASTER_DOCUMENTATION_SITE_URL = ""
    assert _render("/admin/bitcaster/application/") == ""


def test_renders_nothing_for_popup() -> None:
    assert _render("/admin/bitcaster/application/", is_popup=True) == ""
