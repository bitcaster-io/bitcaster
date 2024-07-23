from unittest.mock import Mock

import pytest
from testutils.factories.social import SocialProviderFactory

from bitcaster.social.models import Provider
from bitcaster.social.strategy import BitcasterStrategy

pytestmark = pytest.mark.django_db


def test_social_strategy_generic_setting() -> None:
    s = BitcasterStrategy(Mock(), Mock())
    assert s.get_setting("SOCIAL_AUTH_STRATEGY") == "bitcaster.social.strategy.BitcasterStrategy"


def test_social_strategy_provider_setting() -> None:
    SocialProviderFactory(provider=Provider.GITHUB, configuration={"SOCIAL_AUTH_GITHUB_KEY": "123"})
    s = BitcasterStrategy(Mock(), Mock())
    assert s.get_setting("SOCIAL_AUTH_GITHUB_KEY") == "123"


def test_social_strategy_cache() -> None:
    SocialProviderFactory(provider=Provider.GITHUB, configuration={"SOCIAL_AUTH_GITHUB_KEY": "123"})
    s = BitcasterStrategy(Mock(), Mock())
    assert s.get_setting("SOCIAL_AUTH_GITHUB_KEY") == "123"
    assert s.get_setting("SOCIAL_AUTH_GITHUB_KEY") == "123"


def test_social_strategy_error() -> None:
    s = BitcasterStrategy(Mock(), Mock())
    with pytest.raises(AttributeError):
        assert s.get_setting("SOCIAL_AUTH_XXX_KEY") == "123"


def test_social_strategy_missing() -> None:
    s = BitcasterStrategy(Mock(), Mock())
    with pytest.raises(ValueError) as e:
        s.get_setting("SOCIAL_AUTH_GITLAB_KEY")
        assert e.message == "111"  # type: ignore[attr-defined]


def test_social_strategy_url() -> None:
    SocialProviderFactory(provider=Provider.FACEBOOK, configuration={"SOCIAL_AUTH_FACEBOOK_URL": "login"})
    s = BitcasterStrategy(Mock(), Mock())
    s.get_setting("SOCIAL_AUTH_FACEBOOK_URL")
