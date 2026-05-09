import requests

import pytest
from unittest.mock import patch

from strategy_field.utils import fqn

from bitcaster.dispatchers import XDispatcher
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_x_send_success(mail_payload: requests.Response) -> None:
    ch = Channel(
        dispatcher=fqn(XDispatcher),
        config={
            "consumer_key": "key",
            "consumer_key_secret": "secret",
            "access_token": "token",
            "access_token_secret": "token_secret",
        },
    )
    with patch("requests_oauthlib.OAuth1Session.post") as mock_post:
        mock_response = requests.Response()
        mock_response.status_code = 201
        mock_response._content = b'{"data": {"id": "123", "text": "Hello"}}'
        mock_post.return_value = mock_response

        assert XDispatcher(ch).send("ignored", mail_payload)
        mock_post.assert_called_once_with("https://api.twitter.com/2/tweets", json={"text": "message"})


def test_x_send_failure(mail_payload: requests.Response) -> None:
    ch = Channel(
        dispatcher=fqn(XDispatcher),
        config={
            "consumer_key": "key",
            "consumer_key_secret": "secret",
            "access_token": "token",
            "access_token_secret": "token_secret",
        },
    )
    with patch("requests_oauthlib.OAuth1Session.post") as mock_post:
        mock_response = requests.Response()
        mock_response.status_code = 403
        mock_response._content = b'{"errors": [{"message": "Forbidden"}]}'
        mock_post.return_value = mock_response

        with pytest.raises(DispatcherError, match="Failed to post to X"):
            XDispatcher(ch).send("ignored", mail_payload)


def test_x_send_network_error(mail_payload: requests.Response) -> None:
    ch = Channel(
        dispatcher=fqn(XDispatcher),
        config={
            "consumer_key": "key",
            "consumer_key_secret": "secret",
            "access_token": "token",
            "access_token_secret": "token_secret",
        },
    )
    with patch("requests_oauthlib.OAuth1Session.post") as mock_post:
        mock_post.side_effect = requests.ConnectionError("Timeout")

        with pytest.raises(DispatcherError, match="Error sending message"):
            XDispatcher(ch).send("ignored", mail_payload)


def test_x_truncates_long_message(mail_payload: requests.Response) -> None:
    ch = Channel(
        dispatcher=fqn(XDispatcher),
        config={
            "consumer_key": "key",
            "consumer_key_secret": "secret",
            "access_token": "token",
            "access_token_secret": "token_secret",
        },
    )
    long_text = "x" * 500
    mail_payload.message = long_text

    with patch("requests_oauthlib.OAuth1Session.post") as mock_post:
        mock_response = requests.Response()
        mock_response.status_code = 201
        mock_response._content = b"{}"
        mock_post.return_value = mock_response

        XDispatcher(ch).send("ignored", mail_payload)
        args, kwargs = mock_post.call_args
        assert len(kwargs["json"]["text"]) == 280


def test_x_missing_config(mail_payload: requests.Response) -> None:
    ch = Channel(dispatcher=fqn(XDispatcher), config={})

    with pytest.raises(DispatcherError):
        XDispatcher(ch).send("ignored", mail_payload)


def test_x_extra_config_info() -> None:
    ch = Channel(dispatcher=fqn(XDispatcher), config={})
    info = XDispatcher(ch).get_extra_config_info()
    assert "280 characters" in info
    assert "developer.x.com" in info
    assert "Read and Write" in info
