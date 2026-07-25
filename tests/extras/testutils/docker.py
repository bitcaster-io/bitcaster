import subprocess
from dataclasses import dataclass

from testinfra.host import Host


@dataclass
class ContainerLogs:
    stdout: list[str]
    stderr: list[str]
    offset: int

    def __repr__(self) -> str:
        return "\n".join(self.stdout) + "\n".join(self.stderr)

    def __contains__(self, item):
        return item in str(self.stdout) or item in str(self.stderr)


class ContainerHost:
    def __init__(self, host: Host, container_id: str) -> None:
        self.host = host
        self.container_id = container_id
        self.bookmarks: dict[str, ContainerLogs] = {}
        self.offset: int = 0
        self._stderr_offset: int = 0

    def run(self, *args, **kwargs):
        return self.host.run(*args, **kwargs)

    def logs(self) -> ContainerLogs:
        ret = subprocess.run(
            ["docker", "logs", self.container_id],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        stdout_lines = ret.stdout.split("\n")
        stderr_lines = ret.stderr.split("\n")

        return ContainerLogs(stdout_lines, stderr_lines, 0)

    def lastlog(self) -> ContainerLogs:
        ret = subprocess.run(
            ["docker", "logs", self.container_id],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        stdout_lines = ret.stdout.split("\n")
        stderr_lines = ret.stderr.split("\n")

        new_stdout = stdout_lines[self.offset :]
        new_stderr = stderr_lines[self._stderr_offset :]

        self.offset = len(stdout_lines)
        self._stderr_offset = len(stderr_lines)

        return ContainerLogs(new_stdout, new_stderr, self.offset)
