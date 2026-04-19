import pytest

from bitcaster.utils.shortcuts import render_message


def test_render_message_empty():
    assert render_message(None, {}) == ""
    assert render_message("", {}) == ""


@pytest.mark.django_db
def test_render_message():
    content = "Hello {{ name }}"
    context = {"name": "World"}
    assert render_message(content, context) == "Hello World"


@pytest.mark.django_db
def test_render_message_with_tags():
    # bitcaster and attachments tags are loaded automatically by render_message
    content = "Hello"
    context = {}
    assert render_message(content, context) == "Hello"
