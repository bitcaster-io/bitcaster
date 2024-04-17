from unittest.mock import Mock

import pytest
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


def test_social_strategy_cache(db):
    SocialProviderFactory(provider=Provider.GITHUB, configuration={"SOCIAL_AUTH_GITHUB_KEY": "123"})
    s = BitcasterStrategy(Mock(), Mock())
    assert s.get_setting("SOCIAL_AUTH_GITHUB_KEY") == "123"
    assert s.get_setting("SOCIAL_AUTH_GITHUB_KEY") == "123"


def test_social_strategy_error(db):
    s = BitcasterStrategy(Mock(), Mock())
    with pytest.raises(AttributeError):
        assert s.get_setting("SOCIAL_AUTH_XXX_KEY") == "123"


def test_social_strategy_missing(db):
    s = BitcasterStrategy(Mock(), Mock())
    with pytest.raises(ValueError) as e:
        s.get_setting("SOCIAL_AUTH_GITLAB_KEY")
        assert e.message == "111"


def test_social_strategy_url(db):
    SocialProviderFactory(provider=Provider.FACEBOOK, configuration={"SOCIAL_AUTH_FACEBOOK_URL": "login"})
    s = BitcasterStrategy(Mock(), Mock())
    s.get_setting("SOCIAL_AUTH_FACEBOOK_URL")
