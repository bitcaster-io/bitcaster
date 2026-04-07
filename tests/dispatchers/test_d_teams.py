from unittest.mock import Mock, patch

import pytest
import requests
from requests import Response

from bitcaster.dispatchers.teams import TeamsDispatcher
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture
def channel() -> Channel:
    return Channel(config={"webhook_url": "https://outlook.office.com/webhook/xxx"})


def test_teams_send_success(channel: Channel) -> None:
    dispatcher = TeamsDispatcher(channel)
    payload = Mock(subject="Test Subject", message="Test Message", html_message=None)

    with patch("requests.Session.post") as mock_post:
        mock_response = Response()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        assert dispatcher.send("address", payload)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "https://outlook.office.com/webhook/xxx"

        # Verify Adaptive Card structure
        json_body = kwargs["json"]
        assert json_body["type"] == "message"
        assert len(json_body["attachments"]) == 1
        content = json_body["attachments"][0]["content"]
        assert content["type"] == "AdaptiveCard"

        # Check body elements
        body_elements = content["body"]
        assert body_elements[0]["text"] == "Test Subject"
        assert body_elements[2]["text"] == "Test Message"


def test_teams_send_failure(channel: Channel) -> None:
    dispatcher = TeamsDispatcher(channel)
    payload = Mock(subject="Test Subject", message="Test Message", html_message=None)

    with patch("requests.Session.post") as mock_post:
        mock_response = Response()
        mock_response.status_code = 400
        mock_response._content = b"Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(DispatcherError) as excinfo:
            dispatcher.send("address", payload)
        assert "Failed to send to Teams" in str(excinfo.value)


def test_teams_send_network_error(channel: Channel) -> None:
    dispatcher = TeamsDispatcher(channel)
    payload = Mock(subject="Test Subject", message="Test Message", html_message=None)

    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = requests.RequestException("Connection error")

        with pytest.raises(DispatcherError) as excinfo:
            dispatcher.send("address", payload)
        assert "Error sending message" in str(excinfo.value)


def test_teams_missing_config() -> None:
    channel = Channel(config={})
    dispatcher = TeamsDispatcher(channel)
    payload = Mock(subject="Test Subject", message="Test Message", html_message=None)

    with pytest.raises(DispatcherError) as excinfo:
        dispatcher.send("address", payload)
    assert "Webhook URL not configured" in str(excinfo.value)


def test_teams_test_connection(channel: Channel) -> None:
    dispatcher = TeamsDispatcher(channel)
    assert dispatcher.test_connection() is True


def test_teams_test_connection_fail() -> None:
    channel = Channel(config={})
    dispatcher = TeamsDispatcher(channel)
    assert dispatcher.test_connection() is False
    with pytest.raises(DispatcherError):
        dispatcher.test_connection(raise_exception=True)
