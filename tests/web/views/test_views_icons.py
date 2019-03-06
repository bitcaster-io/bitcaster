import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers import Email, Gmail
from bitcaster.dispatchers.handlers.twitter import TwitterDirectMessage
from bitcaster.web.views.icons import plugin_icon


@pytest.mark.django_db
@pytest.mark.parametrize('target', [fqn(Email), fqn(Gmail), fqn(TwitterDirectMessage)])
def test_plugin_icon(rf, target):
    request = rf.get('/')
    assert plugin_icon(request, target)
