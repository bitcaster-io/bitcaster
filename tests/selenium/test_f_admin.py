from time import sleep
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from testutils.selenium import TestBrowser

if TYPE_CHECKING:
    from bitcaster.models import Event, MessageTemplate

pytestmark = pytest.mark.selenium


@pytest.mark.xdist_group(name="message_template")
def test_login(browser: TestBrowser):
    browser.login()
    browser.click_link("Admin")


@pytest.mark.xdist_group(name="message_template")
@pytest.mark.flaky(max_runs=2)
def test_create_template_message(browser: TestBrowser, event: "Event"):
    from bitcaster.models import MessageTemplate

    channel = event.channels.first()

    browser.login()

    browser.click_link("Admin")
    if not browser.is_element_visible("#nav-sidebar"):
        browser.click('span:contains("dock_to_right")')
    browser.click('//a[contains(., "Message Templates")]')
    browser.click("a[title='Add Message template']")

    browser.type("input[name=name]", "Template Name #1")
    browser.select2_select("id_event", event.name)
    browser.select2_select("id_channel", channel.name)
    browser.scroll_to_bottom()
    browser.click("button[name='_save']")
    browser.assert_admin_message("The Message template .* was added successfully.")
    assert MessageTemplate.objects.filter(name="Template Name #1").exists()


def _set_template_content(browser: TestBrowser, content: str):
    browser.switch_to_frame("#id_html_content_ifr")
    browser.type("#tinymce", content)
    sleep(1)
    browser.send_keys("#tinymce", Keys.TAB)
    sleep(1)
    browser.switch_to_default_content()
    browser.wait_for_element_visible("#preview")
    browser.switch_to_frame("#preview")
    sleep(1)
    text = browser.get_element("html>body").text
    browser.switch_to_default_content()
    return text


@pytest.mark.xdist_group(name="message_template")
@pytest.mark.flaky(max_runs=2)
def test_edit_template_message(browser: TestBrowser, message_template: "MessageTemplate"):
    event = message_template.event
    channel = message_template.channel

    url = reverse("admin:bitcaster_messagetemplate_change", args=(message_template.pk,))
    browser.login()

    browser.open(url)

    browser.click_link("Edit")

    browser.wait_for_element(By.CSS_SELECTOR, "#btn_subject")
    browser.click("#btn_subject")
    browser.type("input[name=subject]", "Subject Test")
    browser.click("button#btn_html")
    text = _set_template_content(browser, "Sample context")

    assert text == "Sample context"
    text = _set_template_content(browser, "Event {{event.name}}")
    assert text == f"Event {event.name}"
    text = _set_template_content(browser, "Address {{assignment.address.value}}")
    assert text == f"Address {browser.admin_user.email}"
    text = _set_template_content(browser, "Channel {{channel.name}}")
    assert text == f"Channel {channel.name}"
