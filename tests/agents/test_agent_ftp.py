from pathlib import Path
from unittest import mock
from unittest.mock import Mock, patch

import pytest
from pytest_localftpserver.servers import PytestLocalFTPServer

from bitcaster.agents.ftp import AgentFTP
from bitcaster.models import Event, Monitor


@pytest.fixture
def agent(event: "Event", server: PytestLocalFTPServer) -> AgentFTP:
    return AgentFTP(
        Mock(
            spec=Monitor,
            event=event,
            config={
                "path": "/",
                "server": f"localhost:{server.server_port}",
                "username": server.username,
                "password": server.password,
                "use_tls": False,
                "add": True,
                "delete": True,
                "change": True,
            },
            data={},
        )
    )


@pytest.fixture
def server(ftpserver: PytestLocalFTPServer) -> PytestLocalFTPServer:
    ftpserver.reset_tmp_dirs()
    ftpserver.put_files(str(Path(__file__).parent / "file1.txt"), style="rel_path", anon=False, return_paths="new")
    ftpserver.put_files(str(Path(__file__).parent / "file2.txt"), style="rel_path", anon=False)
    ftpserver.put_files(str(Path(__file__).parent / "file3.txt"), style="rel_path", anon=False)
    return ftpserver


def test_agent_ftp_config(agent: AgentFTP) -> None:
    assert list(agent.config.keys()) == ["server", "path", "username", "password", "use_tls", "add", "change", "delete"]


def test_agent_ftp_check_with_tls(agent: AgentFTP, server: PytestLocalFTPServer) -> None:
    from unittest.mock import Mock

    from bitcaster.agents.ftp import AgentFTPConfig

    config = AgentFTPConfig(
        data={
            "server": f"localhost:{server.server_port}",
            "path": "/",
            "username": server.username,
            "password": server.password,
            "use_tls": True,
            "add": True,
            "change": True,
            "delete": True,
        }
    )
    assert config.is_valid()
    mock_monitor = Mock()
    mock_monitor.config = config.cleaned_data
    mock_monitor.data = {}
    tls_agent = AgentFTP(mock_monitor)

    with patch("bitcaster.agents.ftp.ftplib.FTP_TLS") as mock_ftp_tls_class:
        mock_ftp_tls = mock_ftp_tls_class.return_value
        mock_ftp_tls.mlsd.return_value = [("file1.txt", {"type": "file"})]
        _ = tls_agent.client
        mock_ftp_tls.connect.assert_called()
        mock_ftp_tls.login.assert_called()


def test_agent_ftp_tls_fallback_to_plain(agent: AgentFTP, server: PytestLocalFTPServer) -> None:
    import ftplib
    from unittest.mock import Mock

    from bitcaster.agents.ftp import AgentFTPConfig

    config = AgentFTPConfig(
        data={
            "server": f"localhost:{server.server_port}",
            "path": "/",
            "username": server.username,
            "password": server.password,
            "add": True,
            "change": True,
            "delete": True,
        }
    )
    assert config.is_valid()
    mock_monitor = Mock()
    mock_monitor.config = config.cleaned_data
    mock_monitor.data = {}
    tls_agent = AgentFTP(mock_monitor)

    with patch("bitcaster.agents.ftp.ftplib.FTP_TLS") as mock_ftp_tls_class:
        mock_ftp_tls_class.side_effect = ftplib.error_perm('500 Command "AUTH" not understood.')
        with patch("bitcaster.agents.ftp.ftplib.FTP_TLS") as mock_ftp_class:
            mock_ftp = mock_ftp_class.return_value
            mock_ftp.mlsd.return_value = [("file1.txt", {"type": "file"})]
            _ = tls_agent.client
            mock_ftp_class.assert_called()
            mock_ftp.connect.assert_called()
            mock_ftp.login.assert_called()


def test_agent_ftp_check(agent: AgentFTP, server: PytestLocalFTPServer) -> None:
    assert agent.monitor.data == {}
    with patch("bitcaster.agents.ftp.ftplib.FTP_TLS"):
        with mock.patch("bitcaster.models.event.Event.trigger") as notify:
            agent.check()
            assert not notify.called
            assert agent.monitor.data["diff"] == {"added": [], "changed": [], "deleted": []}
        with mock.patch.object(agent, "initialize") as initialize:
            with mock.patch("bitcaster.models.event.Event.trigger") as notify:
                agent.check()
                assert not notify.called
                assert not initialize.called
                assert agent.monitor.data["diff"] == {"added": [], "changed": [], "deleted": []}
