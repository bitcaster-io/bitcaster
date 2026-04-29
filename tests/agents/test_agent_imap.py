from email.message import EmailMessage
from email.mime.text import MIMEText
from unittest.mock import MagicMock, patch

import pytest

from bitcaster.agents.imap import AgentImap
from bitcaster.models import Event, Monitor


def create_email(subject: str, body: str, from_addr: str = "sender@example.com") -> bytes:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["Date"] = "Mon, 29 Apr 2026 10:00:00 +0000"
    return msg.as_bytes()


@pytest.fixture
def monitor(event: "Event") -> MagicMock:
    mon = MagicMock(spec=Monitor)
    mon.event = event
    mon.config = {
        "server": "imap.example.com",
        "port": 993,
        "username": "user@example.com",
        "password": "password",
        "use_ssl": True,
        "folder": "INBOX",
        "subject_pattern": r"Alert: (?P<alert_type>\w+) - (?P<severity>\w+)",
        "body_pattern": r"Error: (?P<error_msg>.+)",
    }
    mon.data = {"processed_ids": []}
    return mon


@pytest.fixture
def agent(monitor: MagicMock) -> AgentImap:
    return AgentImap(monitor)


def test_agent_imap_config_subject_pattern_invalid() -> None:
    from bitcaster.agents.imap import AgentImapConfig

    cfg = AgentImapConfig(data={"subject_pattern": "[invalid"})
    assert not cfg.is_valid()
    assert "subject_pattern" in cfg.errors


def test_agent_imap_config_body_pattern_invalid() -> None:
    from bitcaster.agents.imap import AgentImapConfig

    cfg = AgentImapConfig(data={"subject_pattern": r"\w+", "body_pattern": "[invalid"})
    assert not cfg.is_valid()
    assert "body_pattern" in cfg.errors


def test_agent_imap_config_valid() -> None:
    from bitcaster.agents.imap import AgentImapConfig

    cfg = AgentImapConfig(
        data={
            "server": "imap.example.com",
            "port": 993,
            "username": "user",
            "password": "pass",
            "folder": "INBOX",
            "subject_pattern": r"(?P<type>\w+)",
        }
    )
    assert cfg.is_valid()


def test_agent_imap_extract_fields_match(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Critical - High", "Error: Disk full")
    import email
    from email.parser import BytesParser

    msg = BytesParser(policy=email.policy.default).parsebytes(email_bytes)
    fields = agent.extract_fields(msg)
    assert fields is not None
    assert fields["alert_type"] == "Critical"
    assert fields["severity"] == "High"
    assert fields["error_msg"] == "Disk full"
    assert fields["subject"] == "Alert: Critical - High"
    assert fields["from"] == "sender@example.com"


def test_agent_imap_extract_fields_no_match(agent: AgentImap) -> None:
    email_bytes = create_email("Random subject", "No pattern here")
    import email
    from email.parser import BytesParser

    msg = BytesParser(policy=email.policy.default).parsebytes(email_bytes)
    fields = agent.extract_fields(msg)
    assert fields is None


def test_agent_imap_check_triggers_event(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("Alert: Warning - Medium", "Error: CPU high")

    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check()
            assert trigger.called
            call_kwargs = trigger.call_args
            context = call_kwargs.kwargs.get("context") or call_kwargs[1].get("context")
            assert context["alert_type"] == "Warning"
            assert context["severity"] == "Medium"


def test_agent_imap_check_no_match_no_trigger(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("No match here", "Random body")

    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check()
            assert not trigger.called


def test_agent_imap_changes_detected_true(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")

    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        assert agent.changes_detected() is True


def test_agent_imap_changes_detected_false(agent: AgentImap) -> None:
    email_bytes = create_email("No match", "Body")

    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        assert agent.changes_detected() is False


def test_agent_imap_no_ssl(agent: AgentImap, monitor: MagicMock) -> None:
    monitor.config["use_ssl"] = False
    with patch("imaplib.IMAP4") as mock_imap:
        instance = mock_imap.return_value
        instance.search.return_value = ("OK", [b""])
        instance.select.return_value = ("OK", [b"0"])
        agent.connect()
        mock_imap.assert_called_once_with("imap.example.com", 993)


def test_agent_imap_fetch_unseen(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        emails = agent.fetch_unseen(mock_client)
        assert len(emails) == 1
        assert emails[0][0] == "1"


def test_agent_imap_connect_ssl(agent: AgentImap) -> None:
    with patch("imaplib.IMAP4_SSL") as mock_ssl:
        agent.config["use_ssl"] = True
        agent.connect()
        mock_ssl.assert_called_once_with("imap.example.com", 993)


def test_agent_imap_notify(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.notify()
            assert trigger.called


def test_agent_imap_check_update_false(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor, "save") as save:
            agent.check(update=False)
            assert not save.called


def test_agent_imap_already_processed(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    monitor.data = {"processed_ids": ["1"]}
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check()
            assert not trigger.called


def test_agent_imap_fetch_unseen_search_not_ok(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("NO", [b""])
    mock_client.select.return_value = ("OK", [b"0"])
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_fetch_unseen_empty_messages(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b""])
    mock_client.select.return_value = ("OK", [b"0"])
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_fetch_unseen_invalid_fetch_data(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [b"invalid"])  # Not a tuple
    mock_client.select.return_value = ("OK", [b"1"])
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_multipart_email(agent: AgentImap, monitor: MagicMock) -> None:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Alert: Info - Low"
    msg["From"] = "sender@example.com"
    msg.attach(MIMEText("Plain text body Error: Multipart test", "plain"))
    msg.attach(MIMEText("<html>HTML body</html>", "html"))

    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, msg.as_bytes())])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        emails = agent.fetch_unseen(mock_client)
        assert len(emails) == 1
        fields = agent.extract_fields(emails[0][1])
        assert fields is not None
        assert "Multipart test" in fields.get("error_msg", "")


def test_agent_imap_check_logout_exception(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])
    mock_client.logout.side_effect = Exception("Logout failed")

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check()  # Should not raise
            assert trigger.called


def test_agent_imap_changes_detected_logout_exception(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])
    mock_client.logout.side_effect = Exception("Logout failed")

    with patch.object(agent, "connect", return_value=mock_client):
        result = agent.changes_detected()
        assert result is True


def test_agent_imap_changes_detected_already_processed(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    agent.monitor.data = {"processed_ids": ["1"]}
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        result = agent.changes_detected()
        assert result is False


def test_agent_imap_fetch_unseen_search_fails(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("NO", None)
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_extract_fields_multipart_no_plain(agent: AgentImap) -> None:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Alert: Info - Low"
    msg.attach(MIMEText("<html>HTML only</html>", "html"))

    fields = agent.extract_fields(msg)
    assert fields is not None
    assert "error_msg" not in fields or fields.get("error_msg") == ""


def test_agent_imap_fetch_unseen_fetch_not_ok(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("NO", None)
    mock_client.select.return_value = ("OK", [b"1"])
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_fetch_unseen_fetch_data_not_tuple(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", ["not a tuple"])
    mock_client.select.return_value = ("OK", [b"1"])
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_fetch_unseen_fetch_data_wrong_type(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, "not bytes")])
    mock_client.select.return_value = ("OK", [b"1"])
    result = agent.fetch_unseen(mock_client)
    assert result == []


def test_agent_imap_fetch_unseen_fetch_result_not_emailmessage(agent: AgentImap) -> None:
    # Test that _parse_email returns None for bytes without Subject
    result = agent._parse_email(b"not a valid email")
    assert result is None


def test_agent_imap_parse_email_valid(agent: AgentImap) -> None:
    email_bytes = create_email("Test", "Body")
    result = agent._parse_email(email_bytes)
    assert result is not None
    assert isinstance(result, EmailMessage)


def test_agent_imap_parse_email_invalid(agent: AgentImap) -> None:
    # Empty bytes should not produce a valid email with Subject
    result = agent._parse_email(b"")
    assert result is None


def test_agent_imap_parse_email_no_subject(agent: AgentImap) -> None:
    # BytesParser creates message but without Subject header
    result = agent._parse_email(b"Content-Type: text/plain\n\nBody only")
    assert result is None


def test_agent_imap_parse_email_exception(agent: AgentImap) -> None:
    # Simulate an exception during parsing
    with patch("bitcaster.agents.imap.BytesParser.parsebytes", side_effect=Exception("Parse error")):
        result = agent._parse_email(b"test")
        assert result is None


def test_agent_imap_extract_fields_no_subject_pattern_match(agent: AgentImap) -> None:
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "No match here"
    fields = agent.extract_fields(msg)
    assert fields is None


def test_agent_imap_extract_fields_not_multipart(agent: AgentImap) -> None:
    # Use create_email to get proper EmailMessage object
    email_bytes = create_email("Alert: Info - Low", "Error: Single part test")
    import email
    from email.parser import BytesParser

    msg = BytesParser(policy=email.policy.default).parsebytes(email_bytes)
    fields = agent.extract_fields(msg)
    assert fields is not None
    assert fields.get("error_msg") == "Single part test"


def test_agent_imap_extract_fields_multipart_no_text_plain(agent: AgentImap) -> None:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg["Subject"] = "Alert: Info - Low"
    msg.attach(MIMEText("<html>HTML only</html>", "html"))
    fields = agent.extract_fields(msg)
    assert fields is not None
    # No plain text, so body_pattern should not match
    assert "error_msg" not in fields or fields.get("error_msg") == ""


def test_agent_imap_extract_fields_with_body_pattern_no_match(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Info - Low", "No error here")
    import email
    from email.parser import BytesParser

    msg = BytesParser(policy=email.policy.default).parsebytes(email_bytes)
    fields = agent.extract_fields(msg)
    assert fields is not None
    # Body doesn't match the error pattern
    assert "error_msg" not in fields


def test_agent_imap_extract_fields_no_body_pattern(agent: AgentImap, monitor: MagicMock) -> None:
    # Reconfigure agent without body_pattern
    monitor.config = {
        "server": "imap.example.com",
        "port": 993,
        "username": "user@example.com",
        "password": "password",
        "use_ssl": True,
        "folder": "INBOX",
        "subject_pattern": r"Alert: (?P<alert_type>\w+) - (?P<severity>\w+)",
        "body_pattern": "",  # No body pattern
    }
    email_bytes = create_email("Alert: Info - Low", "Some body")
    import email
    from email.parser import BytesParser

    msg = BytesParser(policy=email.policy.default).parsebytes(email_bytes)
    fields = agent.extract_fields(msg)
    assert fields is not None
    assert fields["alert_type"] == "Info"
    assert "error_msg" not in fields


def test_agent_imap_check_no_matches(agent: AgentImap, monitor: MagicMock) -> None:
    # Email that doesn't match the subject pattern
    email_bytes = create_email("No match", "Body")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check()
            assert not trigger.called
            # stored_ids should remain empty
            assert agent.monitor.data == {"processed_ids": [], "last_check": ""}


def test_agent_imap_extract_fields_multipart_content_not_string(agent: AgentImap) -> None:
    from email import policy
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.parser import BytesParser

    # Create a multipart message
    msg = MIMEMultipart()
    msg["Subject"] = "Alert: Info - Low"
    text_part = MIMEText("Error: Test message", "plain")
    msg.attach(text_part)

    # Parse it properly
    email_bytes = msg.as_bytes()
    parsed = BytesParser(policy=policy.default).parsebytes(email_bytes)

    fields = agent.extract_fields(parsed)
    assert fields is not None
    assert fields.get("error_msg") == "Test message"


def test_agent_imap_extract_fields_non_multipart_content_not_string(agent: AgentImap) -> None:
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "Alert: Info - Low"
    msg.set_content("Error: Test content")

    fields = agent.extract_fields(msg)
    assert fields is not None
    assert fields.get("error_msg") == "Test content"


def test_agent_imap_fetch_unseen_no_valid_emails(agent: AgentImap) -> None:
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    # Fetch returns invalid data (no Subject)
    mock_client.fetch.return_value = ("OK", [(None, b"invalid email bytes")])
    mock_client.select.return_value = ("OK", [b"1"])

    result = agent.fetch_unseen(mock_client)
    # Should return empty list since email is invalid
    assert len(result) == 0


def test_agent_imap_changes_detected_no_match(agent: AgentImap) -> None:
    # Email exists but doesn't match pattern
    email_bytes = create_email("No match", "Body")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        result = agent.changes_detected()
        assert result is False


def test_agent_imap_notify_method(agent: AgentImap, monitor: MagicMock) -> None:
    with patch.object(agent, "check") as mock_check:
        agent.notify()
        mock_check.assert_called_once_with(notify=True, update=False)


def test_agent_imap_changes_detected_with_match(agent: AgentImap) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        result = agent.changes_detected()
        assert result is True


def test_agent_imap_check_notify_false(agent: AgentImap, monitor: MagicMock) -> None:
    email_bytes = create_email("Alert: Info - Low", "Error: Test")
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b"1"])
    mock_client.fetch.return_value = ("OK", [(None, email_bytes)])
    mock_client.select.return_value = ("OK", [b"1"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check(notify=False)
            assert not trigger.called


def test_agent_imap_extract_fields_multipart_content_bytes(agent: AgentImap) -> None:
    from email.message import EmailMessage

    # Create message and mock get_content to return bytes
    msg = EmailMessage()
    msg["Subject"] = "Alert: Info - Low"
    msg.set_content("Error: Test message", subtype="plain")

    # Mock get_content to return bytes instead of str
    with patch.object(msg, "get_content", return_value=b"bytes content"):
        fields = agent.extract_fields(msg)
        assert fields is not None
        # body_pattern won't match because content is bytes, not str
        assert "error_msg" not in fields or fields.get("error_msg") == ""


def test_agent_imap_extract_fields_non_multipart_content_bytes(agent: AgentImap) -> None:
    from email.message import EmailMessage

    msg = EmailMessage()
    msg["Subject"] = "Alert: Info - Low"
    msg.set_content("Error: Test", subtype="plain")

    # Mock get_content to return bytes
    with patch.object(msg, "get_content", return_value=b"bytes content"):
        fields = agent.extract_fields(msg)
        assert fields is not None
        assert "error_msg" not in fields or fields.get("error_msg") == ""


def test_agent_imap_check_no_notify_empty_matches(agent: AgentImap, monitor: MagicMock) -> None:
    # No emails found
    mock_client = MagicMock()
    mock_client.search.return_value = ("OK", [b""])
    mock_client.select.return_value = ("OK", [b"0"])

    with patch.object(agent, "connect", return_value=mock_client):
        with patch.object(monitor.event, "trigger") as trigger:
            agent.check()
            assert not trigger.called
            # Should still save (update=True by default)
            assert agent.monitor.data == {"processed_ids": [], "last_check": ""}
