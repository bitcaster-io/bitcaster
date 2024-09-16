from unittest import mock
from unittest.mock import Mock

import pytest
from pyfakefs.fake_filesystem import FakeFile, FakeFilesystem

from bitcaster.agents.fs import AgentFileSystem
from bitcaster.models import Event, Monitor


@pytest.fixture()
def monit_path(event: "Event", fs: FakeFilesystem) -> AgentFileSystem:
    fs.reset()
    return AgentFileSystem(Mock(spec=Monitor, config={"event": event.pk, "path": fs.root.path}, data={}))


@pytest.fixture()
def monit_file(event: "Event", fs: FakeFilesystem) -> AgentFileSystem:
    fs.reset()
    ff: FakeFile = fs.create_file("dir1/file.txt")
    return AgentFileSystem(Mock(spec=Monitor, config={"event": event.pk, "path": ff.path}, data={}))


def test_agent_fs_config(monit_path: AgentFileSystem) -> None:
    assert list(monit_path.config.keys()) == [
        "event",
        "path",
        "monitor_add",
        "monitor_change",
        "monitor_deletion",
        "skip_first_run",
    ]


def test_agent_fs_check_dir(monit_path: AgentFileSystem, fs: FakeFilesystem) -> None:
    assert monit_path.monitor.config["path"] == fs.root.path
    assert monit_path.monitor.data == {}
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_path.check()
        assert not notify.called
        assert monit_path.monitor.data
    with mock.patch.object(monit_path, "initialize") as initialize:
        with mock.patch("bitcaster.models.event.Event.trigger") as notify:
            monit_path.check()
            assert not notify.called
            assert not initialize.called
    fs.create_file("aaa/bbb/new_file1.txt")
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_path.check()
        assert notify.called
    assert "/aaa/bbb/new_file1.txt" in monit_path.monitor.data["diff"]


def test_agent_fs_check_file(monit_file: AgentFileSystem, fs: FakeFilesystem) -> None:
    assert monit_file.monitor.data == {}
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_file.check()
        assert not notify.called
        assert monit_file.monitor.data
    with mock.patch.object(monit_file, "initialize") as initialize:
        with mock.patch("bitcaster.models.event.Event.trigger") as notify:
            monit_file.check()
            assert not notify.called
            assert not initialize.called
    fs.utime("dir1/file.txt", (0, 0))
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_file.check()
        assert notify.called
        assert "/dir1/file.txt" in monit_file.monitor.data["diff"]


def test_agent_fs_delete_file(monit_file: AgentFileSystem, fs: FakeFilesystem) -> None:
    monit_file.initialize()
    fs.remove_object("dir1/file.txt")
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_file.check()
        assert notify.called
        assert "/dir1/file.txt" in monit_file.monitor.data["diff"]
