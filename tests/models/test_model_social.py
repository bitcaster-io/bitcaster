from typing import Any

import pytest

from bitcaster.social.models import Provider, SocialProvider


@pytest.fixture
def data(db: Any) -> "list[SocialProvider]":
    from testutils.factories.social import SocialProviderFactory

    return [
        SocialProviderFactory.create(provider=Provider.GITHUB),
        SocialProviderFactory.create(provider=Provider.GOOGLE),
        SocialProviderFactory.create(provider=Provider.MICROSOFT),
    ]


def test_manager(data) -> None:
    assert SocialProvider.objects.as_choices() == [
        ("github", "Github"),
        ("google", "Google"),
        ("microsoft", "Microsoft"),
    ]


def test_code(data) -> None:
    assert data[0].code
