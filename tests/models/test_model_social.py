from typing import Any

import pytest

from bitcaster.social.models import SocialProvider


@pytest.fixture
def data(db: Any) -> "list[SocialProvider]":
    from testutils.factories.social import SocialProviderFactory

    return [
        SocialProviderFactory.create(provider="github", slug="github"),
        SocialProviderFactory.create(provider="google", slug="google"),
        SocialProviderFactory.create(provider="microsoft", slug="microsoft"),
    ]


def test_manager(data) -> None:
    assert SocialProvider.objects.as_choices() == [
        ("github", "Github"),
        ("google", "Google"),
        ("microsoft", "Microsoft"),
    ]


def test_code(data) -> None:
    assert data[0].code
