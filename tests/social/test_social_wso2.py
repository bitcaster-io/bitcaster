from __future__ import annotations

import typing

import pytest
from constance.test.unittest import override_config
from django.urls import reverse
from responses import RequestsMock
from responses.matchers import query_param_matcher, urlencoded_params_matcher
from testutils.factories import GroupFactory, SocialProviderFactory

from bitcaster.social.backend.wso2 import Wso2OAuth2

if typing.TYPE_CHECKING:
    from django.test import Client
    from pytest import MonkeyPatch

    from bitcaster.social.models import SocialProvider


@pytest.fixture(autouse=True)
def group() -> None:
    GroupFactory(name="demo")


@pytest.fixture()
def config() -> SocialProvider:
    from bitcaster.social.models import Provider

    return SocialProviderFactory(
        provider=Provider.OAUTH2,
        configuration={
            "SOCIAL_AUTH_OAUTH2_KEY": "Key1",
            "SOCIAL_AUTH_OAUTH2_SECRET": "Secret1",
            "SOCIAL_AUTH_OAUTH2_AUTHORIZATION_URL": "https://authserver/authorize",
            "SOCIAL_AUTH_OAUTH2_ACCESS_TOKEN_URL": "https://authserver/oauth2/token",
            "SOCIAL_AUTH_OAUTH2_USERINFO_URL": "https://authserver/oauth2/userinfo",
        },
    )


@override_config(NEW_USER_DEFAULT_GROUP="demo")  # type: ignore[misc]
def test_flow(
    config: SocialProvider, client: "Client", mocked_responses: RequestsMock, monkeypatch: "MonkeyPatch"
) -> None:
    STATE = "-state-"
    CODE = "-code-"
    CODE_CHALLENGE = "-challenge-"
    SESSION_STATE = "-session-state-"

    monkeypatch.setattr(Wso2OAuth2, "generate_code_challenge", lambda *a: CODE_CHALLENGE)
    monkeypatch.setattr(Wso2OAuth2, "state_token", lambda s: STATE)

    expected_authorize_url = (
        config.configuration["SOCIAL_AUTH_OAUTH2_AUTHORIZATION_URL"]
        + "?client_id="
        + config.configuration["SOCIAL_AUTH_OAUTH2_KEY"]
        + "&redirect_uri=http%3A%2F%2Ftestserver%2Fsocial%2Fcomplete%2Foauth2%2F"
        f"&state={STATE}"
        "&response_type=code"
        "&code_challenge_method=S256"
        f"&code_challenge={CODE_CHALLENGE}"
        "&scope=openid"
    )

    # Getting the authserver authorize url
    uri = reverse("social:begin", args=["oauth2"])
    resp = client.get(uri)
    assert resp.status_code == 302
    assert resp.url == expected_authorize_url  # type: ignore[attr-defined]

    # mocking expected calls to authserver
    mocked_responses.add(
        mocked_responses.POST,
        config.configuration["SOCIAL_AUTH_OAUTH2_ACCESS_TOKEN_URL"],
        json={
            "access_token": "-access-token-",
            "refresh_token": "-refresh-token",
            "scope": "openid",
            "id_token": "-super-long-id-token-",
            "token_type": "Bearer",
            "expires_in": 2569,
        },
        match=[
            urlencoded_params_matcher(
                params={
                    "grant_type": "authorization_code",
                    "code": CODE,
                    "redirect_uri": "http://testserver/social/complete/oauth2/",
                    "client_id": config.configuration["SOCIAL_AUTH_OAUTH2_KEY"],
                    "client_secret": config.configuration["SOCIAL_AUTH_OAUTH2_SECRET"],
                    "code_verifier": client.session["oauth2_code_verifier"],
                    "code_challenge": client.session["oauth2_code_verifier"],
                    "code_method": "S256",
                },
            )
        ],
    )

    mocked_responses.add(
        mocked_responses.GET,
        config.configuration["SOCIAL_AUTH_OAUTH2_USERINFO_URL"],
        json={"given_name": "Donald", "family_name": "Duck", "sub": "donald.duck@scroogeville.disney"},
        match=[query_param_matcher(params={"access_token": "-access-token-"})],
    )

    uri = reverse("social:complete", args=["oauth2"])
    uri = f"{uri}?code={CODE}&state={STATE}&session_state={SESSION_STATE}"
    resp = client.get(uri)

    assert (
        resp.wsgi_request.user.email,  # type: ignore[union-attr]
        resp.wsgi_request.user.first_name,  # type: ignore[union-attr]
        resp.wsgi_request.user.last_name,  # type: ignore[union-attr]
    ) == (
        "donald.duck@scroogeville.disney",
        "Donald",
        "Duck",
    )

    from bitcaster.models import User

    assert resp.wsgi_request.user == User.objects.get(
        first_name="Donald", last_name="Duck", email="donald.duck@scroogeville.disney"
    )
