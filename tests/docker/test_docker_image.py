import pytest

pytestmark = pytest.mark.docker


def test_python_version(docker_container) -> None:
    result = docker_container.run("python3 --version")
    assert result.rc == 0
    assert "3.13" in result.stdout


def test_uwsgi_installed(docker_container) -> None:
    assert docker_container.run("which uwsgi").rc == 0


def test_bitcaster_user(docker_container) -> None:
    user = docker_container.user("bitcaster")
    assert user.exists
    assert user.uid == 1000


def test_os4d_group(docker_container) -> None:
    group = docker_container.group("os4d")
    assert group.exists
    assert group.gid == 1024


def test_pythonpath(docker_container) -> None:
    result = docker_container.run("echo $PYTHONPATH")
    assert "/venv/lib/python3.13" in result.stdout


def test_bitcaster_cli(docker_container) -> None:
    result = docker_container.run("bc --version")
    assert result.rc == 0


def test_bitcaster_code_folder(docker_container) -> None:
    result = docker_container.run("ls /code")
    assert result.rc == 2
    result = docker_container.run("ls /")
    assert "code" not in result.stdout


def test_bitcaster_release(docker_container) -> None:
    result = docker_container.run("cat /RELEASE")
    assert result.rc == 0

    result = docker_container.run("release-info.sh")
    assert result.rc == 0
