from typing import Any

import pytest

from bitcaster.social.models import SocialProvider


@pytest.fixture
def data(db: Any) -> "list[SocialProvider]":
    from testutils.factories.social import SocialProviderFactory

    return [
        SocialProviderFactory.create(provider="github"),
        SocialProviderFactory.create(provider="google"),
        SocialProviderFactory.create(provider="microsoft"),
    ]


def test_manager(data) -> None:
    choices = SocialProvider.objects.as_choices()
    assert len(choices) == 3
    assert all(k.isdigit() for k, _ in choices)
    assert {v for _, v in choices} == {"Github", "Google", "Microsoft"}


def test_code(data) -> None:
    assert data[0].code
