import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers import Email, Gmail
from bitcaster.dispatchers.handlers.twitter import TwitterDirectMessage
from bitcaster.web.views.icons import channel_icon, plugin_icon


@pytest.mark.django_db
@pytest.mark.parametrize('target', [fqn(Email), fqn(Gmail), fqn(TwitterDirectMessage)])
def test_plugin_icon(rf, target):
    request = rf.get('/')
    assert plugin_icon(request, target)


@pytest.mark.django_db
def test_channel_icon(rf, channel1):
    request = rf.get('/')
    assert channel_icon(request, channel1.pk)
