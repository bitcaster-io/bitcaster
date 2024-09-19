from pathlib import Path
from unittest import mock
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from pyfakefs.fake_filesystem import FakeFile, FakeFilesystem
from pytest_django.fixtures import SettingsWrapper

from bitcaster.agents.fs import AgentFileSystem, resolve_path, validate_path
from bitcaster.models import Event, Monitor


@pytest.fixture()
def monit_path(event: "Event", fs: FakeFilesystem) -> AgentFileSystem:
    fs.reset()
    fs.create_file("dir1/file1.txt")
    fs.create_file("dir1/file2.txt")
    fs.create_file("dir1/file3.txt")
    return AgentFileSystem(
        Mock(
            spec=Monitor,
            event=event,
            config={"recursive": True, "path": fs.root.path, "add": True, "delete": True, "change": True},
            data={},
        )
    )


@pytest.fixture()
def monit_file(event: "Event", fs: FakeFilesystem) -> AgentFileSystem:
    fs.reset()
    ff: FakeFile = fs.create_file("dir1/file1.txt")
    return AgentFileSystem(
        Mock(
            spec=Monitor,
            event=event,
            config={"recursive": True, "path": ff.path, "add": True, "delete": True, "change": True},
            data={},
        )
    )


def test_agent_fs_config(monit_path: AgentFileSystem) -> None:
    assert list(monit_path.config.keys()) == ["path", "recursive", "add", "change", "delete"]


def test_agent_fs_check_dir(monit_path: AgentFileSystem, fs: FakeFilesystem) -> None:
    assert monit_path.monitor.config["path"] == fs.root.path
    assert monit_path.monitor.data == {}
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_path.check()
        assert not notify.called
        assert monit_path.monitor.data["diff"] == {"added": [], "changed": [], "deleted": []}
    with mock.patch.object(monit_path, "initialize") as initialize:
        with mock.patch("bitcaster.models.event.Event.trigger") as notify:
            monit_path.check()
            assert not notify.called
            assert not initialize.called
            assert monit_path.monitor.data["diff"] == {"added": [], "changed": [], "deleted": []}

    fs.utime("dir1/file1.txt", (0, 0))
    fs.create_file("aaa/bbb/new_file1.txt")
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_path.check()
        assert notify.called
        assert monit_path.monitor.data["diff"]["deleted"] == []
        assert monit_path.monitor.data["diff"]["changed"] == ["/dir1/file1.txt"]
        assert monit_path.monitor.data["diff"]["added"] == ["/aaa/bbb/new_file1.txt"]


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

    fs.utime("dir1/file1.txt", (0, 0))
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_file.check()
        assert monit_file.monitor.data["diff"]["deleted"] == []
        assert monit_file.monitor.data["diff"]["changed"] == ["/dir1/file1.txt"]
        assert monit_file.monitor.data["diff"]["added"] == []
        assert notify.called


def test_agent_fs_delete_file(monit_file: AgentFileSystem, fs: FakeFilesystem) -> None:
    monit_file.initialize()
    fs.remove_object("dir1/file1.txt")
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_file.check()
        assert notify.called
        assert monit_file.monitor.data["diff"]["deleted"] == ["/dir1/file1.txt"]
        assert monit_file.monitor.data["diff"]["changed"] == []
        assert monit_file.monitor.data["diff"]["added"] == []


def test_agent_fs_test(monit_file: AgentFileSystem, fs: FakeFilesystem) -> None:
    monit_file.initialize()
    with mock.patch("bitcaster.models.event.Event.trigger") as notify:
        monit_file.check(notify=False)
        assert not notify.called


def test_agent_fs_no_update(monit_file: AgentFileSystem, fs: FakeFilesystem) -> None:
    monit_file.initialize()
    with mock.patch("bitcaster.models.monitor.Monitor.save") as save:
        monit_file.check(update=False)
        assert not save.called


def test_agent_validate_config(monit_file: AgentFileSystem, fs: FakeFilesystem, settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_VALIDATOR = lambda s: 1 / 0
    agent: AgentFileSystem = AgentFileSystem(
        Mock(
            spec=Monitor,
            event=Mock(),
            config={"path": fs.root.path, "add": True, "delete": True, "change": True},
            data={},
        )
    )
    with pytest.raises(ValidationError):
        assert agent.config
    settings.AGENT_FILESYSTEM_VALIDATOR = lambda s: True
    assert agent.config

    settings.AGENT_FILESYSTEM_VALIDATOR = "bitcaster.agents.fs.validate_path"
    assert agent.config


@pytest.mark.parametrize(
    "path,expected",
    [
        ("b.txt", "/root/b.txt"),
        ("a/b.txt", "/root/a/b.txt"),
        ("/a/b.txt", "/root/a/b.txt"),
        ("/a/b/../../b.txt", "/root/b.txt"),
        ("/", "/root"),
        ("a/", "/root/a"),
    ],
)
def test_resolve_path_root(path: str, expected: str, settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_ROOT = "/root"
    assert resolve_path(path) == expected


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/root/b.txt", "/root/b.txt"),
        ("/root/a/b.txt", "/root/a/b.txt"),
        ("/root/a/b.txt", "/root/a/b.txt"),
        ("/root/a/b/../../b.txt", "/root/b.txt"),
    ],
)
def test_resolve_path_no_root(path: str, expected: str, settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_ROOT = ""
    assert resolve_path(path) == expected


@pytest.mark.parametrize("path", [__file__, str(Path(__file__).parent), f"{Path(__file__).parent}/"])
def test_validate_path_no_root(path: str, settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_ROOT = None
    validate_path(path)


@pytest.mark.parametrize("path", [__file__, str(Path(__file__).parent), f"{Path(__file__).parent}/"])
def test_validate_path_root(path: str, settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_ROOT = str(Path(__file__).parent)
    validate_path(path)


@pytest.mark.parametrize("path", ["../../"])
def test_validate_path_error(path: str, settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_ROOT = str(Path(__file__).parent)
    with pytest.raises(ValidationError):
        validate_path(path)


#
#
# @pytest.mark.parametrize("path", ["a.txt", "a/b.txt"])
# def test_validate_parents_success(path, settings: "SettingsWrapper", fs: FakeFilesystem) -> None:
#     settings.AGENT_FILESYSTEM_ROOT = str(fs.root)
#     fs.reset()
#     fs.create_file(path)
#     validate_path(path)
#
#
# @pytest.mark.parametrize("path", ["..", "/a.txt"])
# def test_validate_parents_fail(path, settings: "SettingsWrapper", fs: "FakeFilesystem") -> None:
#     settings.AGENT_FILESYSTEM_ROOT = str(fs.root)
#     with pytest.raises(ValidationError):
#         validate_path(path)
