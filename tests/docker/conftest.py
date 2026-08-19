import logging
import subprocess

import testinfra

import pytest
from testutils.docker import ContainerHost

logging.getLogger("testinfra").disabled = True
logging.getLogger("testinfra").propagate = False

NETWORK_NAME = "bitcaster-test-net"


SERVER_NAMES = {
    "pg": "bitcaster-test-pg",
    "redis": "bitcaster-test-redis",
    "server": "bitcaster-test-server",
}


def _cleanup() -> None:
    for name in SERVER_NAMES.values():
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, check=False)
    result = subprocess.run(
        ["docker", "network", "inspect", NETWORK_NAME, "--format", "{{range .Containers}}{{.Name}} {{end}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        for cname in result.stdout.strip().split():
            subprocess.run(
                ["docker", "network", "disconnect", "-f", NETWORK_NAME, cname], capture_output=True, check=False
            )
            subprocess.run(["docker", "rm", "-f", cname], capture_output=True, check=False)
    subprocess.run(["docker", "network", "rm", NETWORK_NAME], capture_output=True, check=False)


@pytest.fixture(scope="session", autouse=True)
def cleanup() -> None:
    _cleanup()
    yield
    _cleanup()


@pytest.fixture(scope="session")
def docker_container():
    image_name = "bitcaster:test"
    build_args = [
        "docker",
        "build",
        "-t",
        image_name,
        "-f",
        "docker/Dockerfile",
        "--build-arg",
        "VERSION=0.0.0",
        "--build-arg",
        "GIT_SHA=test",
        "--build-arg",
        "BUILD_DATE=2026-01-01",
        ".",
    ]
    subprocess.check_call(build_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    container_id = (
        subprocess.check_output(
            [
                "docker",
                "run",
                "-d",
                "--entrypoint",
                "sleep",
                image_name,
                "infinity",
            ],
            stderr=subprocess.DEVNULL,
        )
        .decode()
        .strip()
    )
    yield testinfra.get_host("docker://" + container_id)
    subprocess.check_call(["docker", "rm", "-f", container_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@pytest.fixture(scope="session")
def postgres_container():
    _cleanup()

    network_name = NETWORK_NAME
    pg_name = SERVER_NAMES["pg"]
    subprocess.check_call(
        ["docker", "network", "create", network_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    subprocess.check_output(
        [
            "docker",
            "run",
            "-d",
            "--network",
            network_name,
            "--name",
            pg_name,
            "-e",
            "POSTGRES_USER=bitcaster",
            "-e",
            "POSTGRES_PASSWORD=password",
            "-e",
            "POSTGRES_DB=bitcaster_test",
            "postgres:15",
        ],
        stderr=subprocess.DEVNULL,
    )

    _wait_for_postgres(pg_name)

    yield pg_name
    subprocess.check_call(["docker", "rm", "-f", pg_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


@pytest.fixture(scope="session")
def started_server(postgres_container):
    image_name = "bitcaster:test"
    network_name = NETWORK_NAME
    redis_name = SERVER_NAMES["redis"]
    server_name = SERVER_NAMES["server"]
    pg_name = postgres_container

    build_args = [
        "docker",
        "build",
        "-t",
        image_name,
        "-f",
        "docker/Dockerfile",
        "--build-arg",
        "VERSION=0.0.0",
        "--build-arg",
        "GIT_SHA=test",
        "--build-arg",
        "BUILD_DATE=2026-01-01",
        ".",
    ]

    redis_id = (
        subprocess.check_output(
            [
                "docker",
                "run",
                "-d",
                "--network",
                network_name,
                "--name",
                redis_name,
                "redis:7-alpine",
            ],
            stderr=subprocess.DEVNULL,
        )
        .decode()
        .strip()
    )

    subprocess.check_call(build_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    container_id = (
        subprocess.check_output(
            [
                "docker",
                "run",
                "-d",
                "--network",
                network_name,
                "--name",
                server_name,
                "-p",
                "8003:8000",
                "-e",
                f"DATABASE_URL=postgres://bitcaster:password@{pg_name}:5432/bitcaster_test",
                "-e",
                f"CACHE_URL=redis://{redis_name}:6379/1",
                "-e",
                "SECRET_KEY=test-key-not-for-production",
                "-e",
                f"DRAMATIQ_BROKER=redis://{redis_name}:6379/0",
                "-e",
                "MEDIA_ROOT=/tmp/media",
                "-e",
                "STATIC_ROOT=/tmp/static",
                "-e",
                "BITCASTER_LOGGING_LEVEL=DEBUG",
                "-e",
                "CSRF_COOKIE_SECURE=False",
                "-e",
                "SESSION_COOKIE_SECURE=False",
                "-e",
                "SOCIAL_AUTH_REDIRECT_IS_HTTPS=False",
                "-e",
                "SECURE_SSL_REDIRECT=False",
                "-e",
                "SECURE_HSTS_PRELOAD=0",
                "-e",
                "ALLOWED_HOSTS=localhost,127.0.0.1",
                "-e",
                "ADMIN_EMAIL=admin@example.com",
                "-e",
                "ADMIN_PASSWORD=password",
                "-e",
                "GIT_SHA=test",
                image_name,
                "run",
            ],
            stderr=subprocess.DEVNULL,
        )
        .decode()
        .strip()
    )

    _wait_for_server(container_id)
    yield ContainerHost(
        host=testinfra.get_host("docker://" + container_id),
        container_id=container_id,
    )
    subprocess.check_call(["docker", "rm", "-f", server_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.check_call(["docker", "rm", "-f", redis_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _wait_for_postgres(pg_name, timeout=30):
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(
            ["docker", "exec", pg_name, "pg_isready", "-U", "bitcaster", "-d", "bitcaster_test"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("PostgreSQL did not become ready within timeout")


def _wait_for_server(container_id, timeout=120):
    import time

    deadline = time.time() + timeout
    while time.time() < deadline:
        result = subprocess.run(
            [
                "docker",
                "exec",
                container_id,
                "sh",
                "-c",
                (
                    'python3 -c "import http.client; '
                    "c = http.client.HTTPConnection('localhost', 8000, timeout=5); "
                    "c.request('GET', '/healthcheck/'); "
                    "r = c.getresponse(); "
                    'print(r.status); r.read()"'
                ),
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip().isdigit():
            return
        time.sleep(5)
    logs = subprocess.run(
        ["docker", "logs", "--tail", "30", container_id], capture_output=True, text=True, timeout=5, check=False
    )
    raise RuntimeError(f"Server did not start within timeout\nSTDOUT: {logs.stdout}\nSTDERR: {logs.stderr}")
