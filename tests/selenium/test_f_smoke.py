from pprint import pformat

import pytest
from testutils.liveserver import static_404s
from testutils.selenium import TestBrowser

pytestmark = pytest.mark.selenium


@pytest.mark.xdist_group(name="admin")
def test_admin_pages_no_missing_static(browser: TestBrowser) -> None:
    failures: dict[str, list[str]] = {}

    _visit(browser, "/admin/login/", failures)

    browser.login()
    static_404s.clear()

    for url in _admin_urls():
        _visit(browser, url, failures)

    assert not failures, f"Missing static resources on admin pages:\n{pformat(failures)}"


def _visit(browser: TestBrowser, url: str, failures: dict[str, list[str]]) -> None:
    static_404s.clear()
    browser.open(url)
    browser.wait_for_ready_state_complete()
    if static_404s:
        failures[url] = list(static_404s)


def _admin_urls() -> list[str]:
    from testutils.factories.base import factories_registry

    from django.contrib import admin
    from django.urls import reverse

    urls = ["/admin/"]
    for model in admin.site._registry:
        opts = model._meta
        app_label = opts.app_label
        model_name = opts.model_name
        urls.append(reverse(f"admin:{app_label}_{model_name}_changelist"))
        urls.append(reverse(f"admin:{app_label}_{model_name}_add"))
        factory = factories_registry.get(model)
        if factory is None:
            continue
        instance = factory.create()
        urls.append(reverse(f"admin:{app_label}_{model_name}_change", args=[instance.pk]))
    return urls
