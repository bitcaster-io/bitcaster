import time
from pathlib import Path
from unittest import mock
from unittest.mock import Mock

import pytest
from pytest_localftpserver.servers import PytestLocalFTPServer

from bitcaster.agents.ftp import AgentFTP
from bitcaster.models import Event, Monitor


@pytest.fixture()
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
                "add": True,
                "delete": True,
                "change": True,
            },
            data={},
        )
    )


@pytest.fixture()
def server(ftpserver: PytestLocalFTPServer) -> PytestLocalFTPServer:
    ftpserver.reset_tmp_dirs()
    ftpserver.put_files(str(Path(__file__).parent / "file1.txt"), style="rel_path", anon=False, return_paths="new")
    ftpserver.put_files(str(Path(__file__).parent / "file2.txt"), style="rel_path", anon=False)
    ftpserver.put_files(str(Path(__file__).parent / "file3.txt"), style="rel_path", anon=False)
    return ftpserver


def test_agent_ftp_config(agent: AgentFTP) -> None:
    assert list(agent.config.keys()) == ["server", "path", "username", "password", "add", "change", "delete"]


def test_agent_ftp_check(agent: AgentFTP, server: PytestLocalFTPServer) -> None:
    assert agent.monitor.data == {}
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

    (Path(server.get_local_base_path()) / "file1.txt").write_text(str(time.time()))
    server.put_files(str(Path(__file__).parent / "file4.txt"), style="rel_path", anon=False, overwrite=True)
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        agent.check()
        assert notify.called
    assert agent.monitor.data["diff"]["deleted"] == []
    assert agent.monitor.data["diff"]["changed"] == ["file1.txt"]
    assert agent.monitor.data["diff"]["added"] == ["file4.txt"]
    server.reset_tmp_dirs()
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        agent.check()
        assert notify.called
    assert sorted(agent.monitor.data["diff"]["deleted"]) == ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
