from unittest.mock import Mock

import pytest

from bitcaster.agents.base import Agent

pytestmark = pytest.mark.django_db


def test_base():
    base = Agent()
    assert base


def test_get_options_form(application1):
    base = Agent(Mock(application=application1))
    assert base.get_options_form()
    assert base.get_options_form(data={'abc': 11})


def test_validate_configuration(event1):
    base = Agent(Mock(application=event1.application))
    assert base.validate_configuration({'event': event1.pk})
