# -*- coding: utf-8 -*-
import pytest

from bitcaster.utils.tokens import (
    generate_api_token, generate_subscription_token, generate_token,)


@pytest.mark.django_db
def test_generate_subscription_token(subscription1):
    return generate_subscription_token(subscription1)


def test_generate_api_token():
    assert generate_api_token()


def test_generate_token():
    assert generate_token()
