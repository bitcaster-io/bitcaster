from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By

import pytest
from testutils.selenium import TestBrowser

from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.models import Event, MessageTemplate

pytestmark = pytest.mark.selenium


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


def _set_template_content(browser: TestBrowser, content: str) -> str:
    return browser.execute_script(  # type: ignore[no-any-return]
        """
        var editor = tinymce.activeEditor;
        var renderUrl = document.querySelector('meta[name="render-url"]').getAttribute('content');
        var csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
        var contextEl = document.getElementById('id_context');

        editor.setContent(arguments[0]);

        var payload = {
            content_type: 'text/html',
            content: editor.getContent('id_html_content'),
            context: contextEl ? contextEl.value : '{}',
            recipient: document.getElementById('id_recipient').value,
        };

        var xhr = new XMLHttpRequest();
        xhr.open('POST', renderUrl, false);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.setRequestHeader('X-CSRFToken', csrf);
        xhr.send(new URLSearchParams(payload));

        var iframe = document.getElementById('preview');
        iframe.src = 'about:blank';
        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(xhr.responseText);
        iframe.contentWindow.document.close();

        return iframe.contentDocument.body.innerText;
    """,
        content,
    )


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
