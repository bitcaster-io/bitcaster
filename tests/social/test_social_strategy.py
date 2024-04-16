from unittest.mock import Mock

from testutils.factories.social import SocialProviderFactory

from bitcaster.social.models import Provider
from bitcaster.social.strategy import BitcasterStrategy


def test_social_strategy_generic_setting():
    s = BitcasterStrategy(Mock(), Mock())
    assert s.get_setting("SOCIAL_AUTH_STRATEGY") == "bitcaster.social.strategy.BitcasterStrategy"


def test_social_strategy_provider_setting(db):
    SocialProviderFactory(provider=Provider.GITHUB, configuration={"SOCIAL_AUTH_GITHUB_KEY": "123"})
    s = BitcasterStrategy(Mock(), Mock())
    assert s.get_setting("SOCIAL_AUTH_GITHUB_KEY") == "123"
