import pytest
from testutils.selenium import TestBrowser

pytestmark = pytest.mark.selenium


@pytest.mark.xdist_group(name="admin")
def test_login(browser: TestBrowser):
    browser.login()
    browser.click_link("Admin")


@pytest.mark.flaky(max_runs=2)
def test_left_menu_visible(browser: TestBrowser) -> None:
    browser.login()
    browser.open("/admin/")
    if not browser.is_element_visible("#nav-sidebar"):
        browser.click('span:contains("dock_to_right")')
    assert browser.is_element_visible("#nav-sidebar")
    assert browser.is_text_visible("Occurrences")
    assert browser.is_text_visible("Members")
